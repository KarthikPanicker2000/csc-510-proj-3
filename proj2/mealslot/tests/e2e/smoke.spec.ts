import { expect, test } from "@playwright/test";

test("TC-UC04-01 @p0 completes the default solo spin", async ({
  page,
}) => {
  await page.goto("/");

  await expect(page).toHaveTitle(/MealSlot/i);
  const spinButton = page.getByRole("button", { name: /spin/i });
  await expect(spinButton).toBeVisible();
  await spinButton.click();

  await expect(
    page.getByRole("heading", { name: /Selected Dishes/i }),
  ).toBeVisible();
  await expect(page.getByText("No options")).toHaveCount(0);
});
