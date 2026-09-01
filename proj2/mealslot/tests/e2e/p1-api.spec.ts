import { expect, test, type APIRequestContext } from "@playwright/test";
import { PrismaClient } from "@prisma/client";

import { getTestDatabaseUrl } from "./test-env";

const prisma = new PrismaClient({
  datasources: { db: { url: getTestDatabaseUrl() } },
});

test.afterAll(async () => {
  await prisma.$disconnect();
});

type CreatedParty = {
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

async function createUser(
  request: APIRequestContext,
  authId: string,
  displayName: string,
) {
  const response = await request.post("/api/user/create", {
    data: { auth_id: authId, displayName },
  });
  expect(response.status()).toBe(200);
  return response.json();
}

test("TC-UC16-02 @p1 rejects empty, whitespace-only, and 25-character party nicknames", async ({
  request,
}) => {
  const variants = [
    { label: "empty", nickname: "" },
    { label: "whitespace", nickname: "   " },
    { label: "25 characters", nickname: "A".repeat(25) },
  ];
  const observed: Record<string, number> = {};

  for (const variant of variants) {
    const response = await request.post("/api/party/create", {
      data: { nickname: variant.nickname },
    });
    observed[variant.label] = response.status();
  }

  expect(observed).toEqual({
    empty: 400,
    whitespace: 400,
    "25 characters": 400,
  });
});

test("TC-UC17-02 @p1 rejects malformed and nonexistent party codes without creating memberships", async ({
  request,
}) => {
  const created = await createParty(request, "P1 Join Host");

  for (const malformedCode of ["ABCDE", "ABCDEFG"]) {
    const response = await request.post("/api/party/join", {
      data: { code: malformedCode, nickname: "Rejected Member" },
    });
    expect(response.status()).toBe(400);
  }

  const nonexistent = await request.post("/api/party/join", {
    data: { code: "ZZZZZZ", nickname: "Missing Party Member" },
  });
  expect(nonexistent.status()).toBe(404);
  await expect(nonexistent.json()).resolves.toEqual({ code: "NOT_FOUND" });

  const stateResponse = await request.get(
    `/api/party/state?code=${created.code}`,
  );
  expect(stateResponse.status()).toBe(200);
  const state = await stateResponse.json();
  expect(state.members).toHaveLength(1);
  expect(state.members[0].id).toBe(created.memberId);
});

test("TC-UC14-03 @p1 preserves authoritative membership when the leave operation fails", async ({
  request,
}) => {
  const created = await createParty(request, "P1 Leave Host");
  const joinResponse = await request.post("/api/party/join", {
    data: { code: created.code, nickname: "P1 Leave Member" },
  });
  expect(joinResponse.status()).toBe(200);
  const joined = await joinResponse.json();

  const failedLeave = await request.post("/api/party/leave", {
    data: { memberId: `${joined.memberId}-missing` },
  });
  expect(failedLeave.status()).toBe(500);
  await expect(failedLeave.json()).resolves.toEqual({ code: "INTERNAL" });

  const stateResponse = await request.get(
    `/api/party/state?code=${created.code}`,
  );
  expect(stateResponse.status()).toBe(200);
  const state = await stateResponse.json();
  expect(state.members).toEqual(
    expect.arrayContaining([
      expect.objectContaining({ id: created.memberId }),
      expect.objectContaining({ id: joined.memberId }),
    ]),
  );
});

test("TC-UC08-01 @p1 persists one authenticated favorite exactly once", async ({
  request,
}) => {
  const authId = "p1-favorite-user";
  await createUser(request, authId, "P1 Favorite User");
  const dish = await prisma.dish.findFirst({ orderBy: { id: "asc" } });
  expect(dish).not.toBeNull();

  const save = await request.post("/api/user/saved", {
    data: { authId, savedMeals: [dish!.id] },
  });
  expect(save.status()).toBe(200);
  await expect(save.json()).resolves.toEqual({ savedMeals: [dish!.id] });

  const stored = await prisma.user.findUnique({ where: { auth_id: authId } });
  expect(stored?.savedMeals).toEqual([dish!.id]);
  expect(stored?.savedMeals.filter((id) => id === dish!.id)).toHaveLength(1);
});

test("TC-UC12-01 @p1 resolves authenticated favorites from multiple catalog categories", async ({
  request,
}) => {
  const authId = "p1-browse-user";
  await createUser(request, authId, "P1 Browse User");

  const dishes = await prisma.dish.findMany({ orderBy: { id: "asc" } });
  const first = dishes[0];
  const second = dishes.find((dish) => dish.category !== first?.category);
  expect(first).toBeDefined();
  expect(second).toBeDefined();
  const savedIds = [first!.id, second!.id];

  const save = await request.post("/api/user/saved", {
    data: { authId, savedMeals: savedIds },
  });
  expect(save.status()).toBe(200);

  const catalogResponse = await request.get("/api/dishes");
  expect(catalogResponse.status()).toBe(200);
  const catalog = (await catalogResponse.json()) as Array<{
    id: string;
    category: string;
  }>;
  const resolved = catalog.filter((dish) => savedIds.includes(dish.id));

  expect(resolved.map((dish) => dish.id).sort()).toEqual(savedIds.sort());
  expect(new Set(resolved.map((dish) => dish.category)).size).toBe(2);
  for (const category of new Set(resolved.map((dish) => dish.category))) {
    expect(resolved.filter((dish) => dish.category === category)).toHaveLength(1);
  }
});

test("TC-UC13-01 @p1 removes one authenticated favorite durably without affecting another", async ({
  request,
}) => {
  const authId = "p1-remove-user";
  await createUser(request, authId, "P1 Remove User");
  const dishes = await prisma.dish.findMany({
    orderBy: { id: "asc" },
    take: 2,
  });
  expect(dishes).toHaveLength(2);
  const removed = dishes[0]!;
  const retained = dishes[1]!;

  const initialSave = await request.post("/api/user/saved", {
    data: { authId, savedMeals: [removed.id, retained.id] },
  });
  expect(initialSave.status()).toBe(200);

  const removal = await request.post("/api/user/saved", {
    data: { authId, savedMeals: [retained.id] },
  });
  expect(removal.status()).toBe(200);
  await expect(removal.json()).resolves.toEqual({ savedMeals: [retained.id] });

  const stored = await prisma.user.findUnique({ where: { auth_id: authId } });
  expect(stored?.savedMeals).toEqual([retained.id]);
  expect(stored?.savedMeals).not.toContain(removed.id);
});

test("TC-UC04-03 @p1 verifies party fallback allergen safety when internal spin fails", async () => {
  test.skip(
    true,
    "The unchanged live route has no controllable failure-injection seam for its server-to-server /api/spin call; report as BLOCKED rather than simulating product code.",
  );
});
