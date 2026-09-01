import { expect, test, type Browser, type BrowserContext, type Page } from "@playwright/test";

type PartySession = {
  code: string;
  context: BrowserContext;
  page: Page;
};

async function openPartyContext(browser: Browser): Promise<PartySession> {
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto("/party");
  return { code: "", context, page };
}

async function createParty(browser: Browser, nickname: string): Promise<PartySession> {
  const session = await openPartyContext(browser);
  await session.page.getByPlaceholder("Enter your name").fill(nickname);
  await session.page.getByRole("button", { name: "Create" }).click();

  const codeInput = session.page.getByPlaceholder("------");
  await expect(codeInput).toHaveValue(/^[A-Z0-9]{6}$/);
  session.code = await codeInput.inputValue();
  await expect(session.page.getByText("Party chat", { exact: true })).toBeVisible();
  return session;
}

async function joinParty(
  browser: Browser,
  code: string,
  nickname: string,
): Promise<PartySession> {
  const session = await openPartyContext(browser);
  const codeInput = session.page.getByPlaceholder("------");
  await codeInput.fill(code);
  await session.page.getByPlaceholder("Enter your name").fill(nickname);
  await session.page.getByRole("button", { name: "Join" }).click();
  await expect(session.page.getByText("Party chat", { exact: true })).toBeVisible();
  session.code = code;
  return session;
}

async function spinAsHost(page: Page): Promise<void> {
  const spinButton = page.getByRole("button", { name: /SPIN!/ });
  await expect(spinButton).toBeEnabled();
  await spinButton.click();
  await expect(page.getByRole("link", { name: "YouTube" })).toHaveCount(3);
}

async function closeSessions(...sessions: PartySession[]): Promise<void> {
  await Promise.all(sessions.map((session) => session.context.close()));
}

test("TC-UC03-01 @p1 reaches keep-vote quorum across three party members", async ({
  browser,
}) => {
  const host = await createParty(browser, "P1 Vote Host");
  const memberOne = await joinParty(browser, host.code, "P1 Voter One");
  const memberTwo = await joinParty(browser, host.code, "P1 Voter Two");

  try {
    await spinAsHost(host.page);

    await expect.soft(memberOne.page.getByRole("link", { name: "YouTube" })).toHaveCount(3, {
      timeout: 3_000,
    });
    await expect.soft(memberTwo.page.getByRole("link", { name: "YouTube" })).toHaveCount(3, {
      timeout: 3_000,
    });

    const firstKeep = memberOne.page.getByRole("button", { name: "0" }).nth(0);
    await expect.soft(firstKeep).toBeEnabled({ timeout: 3_000 });
    if (await firstKeep.isEnabled()) await firstKeep.click();

    const secondKeep = memberTwo.page.getByRole("button", { name: "0" }).nth(0);
    await expect.soft(secondKeep).toBeEnabled({ timeout: 3_000 });
    if (await secondKeep.isEnabled()) await secondKeep.click();

    await expect.soft(host.page.getByTitle("Unlock").first()).toBeVisible({
      timeout: 3_000,
    });
  } finally {
    await closeSessions(host, memberOne, memberTwo);
  }
});

test("TC-UC03-03 @p1 switches a member vote from keep to reroll on one slot", async ({
  browser,
}) => {
  const host = await createParty(browser, "P1 Vote Switch Host");

  try {
    await spinAsHost(host.page);
    const keepButtons = host.page.locator("button:has(svg.lucide-thumbs-up)");
    const rerollButtons = host.page.locator("button:has(svg.lucide-rotate-ccw)");
    await expect(keepButtons).toHaveCount(3);
    await expect(rerollButtons).toHaveCount(4);

    const keepVote = keepButtons.nth(0);
    const rerollVote = rerollButtons.nth(0);
    await keepVote.click();
    await expect(keepVote).toContainText("1");
    await expect(rerollVote).toContainText("0");

    await rerollVote.click();

    await expect(keepVote).toContainText("0");
    await expect(rerollVote).toContainText("1");
  } finally {
    await closeSessions(host);
  }
});

test("TC-UC20-01 @p1 exchanges chat messages between two browser sessions", async ({
  browser,
}) => {
  const host = await createParty(browser, "P1 Chat Host");
  const member = await joinParty(browser, host.code, "P1 Chat Member");

  try {
    const hostMessage = `host-to-member-${Date.now()}`;
    await host.page.getByPlaceholder("Message…").fill(hostMessage);
    await host.page.getByRole("button", { name: "Send" }).click();
    await expect(host.page.getByText(hostMessage, { exact: true })).toBeVisible();
    await expect.soft(member.page.getByText(hostMessage, { exact: true })).toBeVisible({
      timeout: 3_000,
    });

    const memberMessage = `member-to-host-${Date.now()}`;
    await member.page.getByPlaceholder("Message…").fill(memberMessage);
    await member.page.getByRole("button", { name: "Send" }).click();
    await expect(member.page.getByText(memberMessage, { exact: true })).toBeVisible();
    await expect.soft(host.page.getByText(memberMessage, { exact: true })).toBeVisible({
      timeout: 3_000,
    });
  } finally {
    await closeSessions(host, member);
  }
});

test("TC-UC20-03 @p1 continues chat over the same-origin fallback when the socket is unavailable", async () => {
  test.skip(
    true,
    "The current E2E build hardcodes NEXT_PUBLIC_WS_URL and the unchanged client exposes no runtime switch to force its BroadcastChannel fallback; report as BLOCKED.",
  );
});
