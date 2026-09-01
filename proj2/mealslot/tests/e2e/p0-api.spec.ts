import { expect, test, type APIRequestContext } from "@playwright/test";

type CreatedParty = {
  code: string;
  partyId: string;
  memberId: string;
  host: boolean;
};

type JoinedParty = {
  code: string;
  partyId: string;
  memberId: string;
};

async function createParty(
  request: APIRequestContext,
  nickname: string,
): Promise<CreatedParty> {
  const response = await request.post("/api/party/create", {
    data: { nickname },
  });
  expect(response.status()).toBe(200);
  return response.json();
}

async function joinParty(
  request: APIRequestContext,
  code: string,
  nickname: string,
): Promise<JoinedParty> {
  const response = await request.post("/api/party/join", {
    data: { code, nickname },
  });
  expect(response.status()).toBe(200);
  return response.json();
}

test("TC-UC04-02 @p0 rejects missing categories and returns a placeholder for an empty category", async ({
  request,
}) => {
  const invalid = await request.post("/api/spin", { data: {} });
  expect(invalid.status()).toBe(400);
  await expect(invalid.json()).resolves.toMatchObject({
    message: "category or categories is required",
  });

  const empty = await request.post("/api/spin", {
    data: { categories: ["category-with-no-dishes"] },
  });
  expect(empty.status()).toBe(200);
  const body = await empty.json();
  expect(body.selection).toHaveLength(1);
  expect(body.selection[0]).toMatchObject({
    name: "No options",
    category: "unknown",
    allergens: [],
  });
});

test("TC-UC09-01 @p0 excludes selected allergens from spin candidates and results", async ({
  request,
}) => {
  const response = await request.post("/api/spin", {
    data: {
      categories: ["dinner", "dinner", "dinner"],
      allergens: ["fish"],
    },
  });

  expect(response.status()).toBe(200);
  const body = await response.json();
  expect(body.selection).toHaveLength(3);

  for (const reel of body.reels as Array<Array<{ allergens: string[] }>>) {
    for (const dish of reel) {
      expect(dish.allergens.map((value) => value.toLowerCase())).not.toContain(
        "fish",
      );
    }
  }

  for (const dish of body.selection as Array<{
    name: string;
    allergens: string[];
  }>) {
    expect(dish.name).not.toBe("No options");
    expect(dish.allergens.map((value) => value.toLowerCase())).not.toContain(
      "fish",
    );
  }
});

test("TC-UC16-01 @p0 creates an active party with the creator as its first member", async ({
  request,
}) => {
  const created = await createParty(request, "Host Alpha");

  expect(created.code).toMatch(/^[A-Z0-9]{6}$/);
  expect(created.host).toBe(true);

  const stateResponse = await request.get(
    `/api/party/state?code=${created.code}`,
  );
  expect(stateResponse.status()).toBe(200);
  const state = await stateResponse.json();

  expect(state.party).toMatchObject({
    id: created.partyId,
    code: created.code,
    isActive: true,
    constraints: {},
  });
  expect(state.members).toEqual([
    expect.objectContaining({
      id: created.memberId,
      nickname: "Host Alpha",
    }),
  ]);
});

test("TC-UC17-01 @p0 joins an active party and exposes both members in party state", async ({
  request,
}) => {
  const created = await createParty(request, "Host Beta");
  const joined = await joinParty(request, created.code, "Member Beta");

  expect(joined).toMatchObject({
    code: created.code,
    partyId: created.partyId,
  });

  const stateResponse = await request.get(
    `/api/party/state?code=${created.code}`,
  );
  expect(stateResponse.status()).toBe(200);
  const state = await stateResponse.json();

  expect(state.members).toHaveLength(2);
  expect(state.members).toEqual(
    expect.arrayContaining([
      expect.objectContaining({
        id: created.memberId,
        nickname: "Host Beta",
      }),
      expect.objectContaining({
        id: joined.memberId,
        nickname: "Member Beta",
      }),
    ]),
  );
});

test("TC-UC02-01 @p0 merges party diets, allergens, budget, and time preferences", async ({
  request,
}) => {
  const created = await createParty(request, "Host Gamma");
  const joined = await joinParty(request, created.code, "Member Gamma");

  const hostUpdate = await request.post("/api/party/update", {
    data: {
      partyId: created.partyId,
      memberId: created.memberId,
      prefs: {
        nickname: "Host Gamma",
        diet: "vegetarian",
        allergens: ["dairy"],
        budgetBand: 2,
        timeBand: 3,
      },
    },
  });
  expect(hostUpdate.status()).toBe(200);

  const memberUpdate = await request.post("/api/party/update", {
    data: {
      partyId: created.partyId,
      memberId: joined.memberId,
      prefs: {
        nickname: "Member Gamma",
        diet: "vegan",
        allergens: ["soy"],
        budgetBand: 1,
        timeBand: 2,
      },
    },
  });
  expect(memberUpdate.status()).toBe(200);
  const merged = await memberUpdate.json();

  expect(merged).toMatchObject({
    merged: {
      diet: ["vegan"],
      budgetBand: 1,
      timeBand: 2,
    },
    conflict: false,
  });
  expect(merged.merged.allergens).toEqual(
    expect.arrayContaining(["dairy", "soy"]),
  );

  const stateResponse = await request.get(
    `/api/party/state?code=${created.code}`,
  );
  expect(stateResponse.status()).toBe(200);
  const state = await stateResponse.json();
  expect(state.party.constraints).toEqual(merged.merged);
});

test("TC-UC14-01 @p0 removes the intended member while the party remains active", async ({
  request,
}) => {
  const created = await createParty(request, "Host Delta");
  const joined = await joinParty(request, created.code, "Member Delta");

  const leave = await request.post("/api/party/leave", {
    data: { memberId: joined.memberId },
  });
  expect(leave.status()).toBe(200);
  await expect(leave.json()).resolves.toEqual({ ok: true });

  const stateResponse = await request.get(
    `/api/party/state?code=${created.code}`,
  );
  expect(stateResponse.status()).toBe(200);
  const state = await stateResponse.json();

  expect(state.party.isActive).toBe(true);
  expect(state.members).toHaveLength(1);
  expect(state.members[0]).toMatchObject({
    id: created.memberId,
    nickname: "Host Delta",
  });
});
