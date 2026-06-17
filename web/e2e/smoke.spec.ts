import { expect, test } from "@playwright/test";

// Core happy path in demo mode (no engine credential): dev-login, walk the 3-step
// new-decision stepper, submit, and land on a rendered verdict detail page.
test("dev login → submit a decision → verdict detail", async ({ page }) => {
  await page.goto("/login");
  await page.locator('input[name="subject"]').fill("e2e@truenorth.local");
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(page).toHaveURL(/\/dashboard/);

  await page.goto("/decisions/new");
  // Step 1 (Type): the default selection is fine — continue.
  await page.getByRole("button", { name: "Continue" }).click();
  // Step 2 (Details): enter the decision question, then continue.
  await page
    .getByPlaceholder(/Should we ship release/)
    .fill("E2E smoke: should we ship the nightly build?");
  await page.getByRole("button", { name: "Continue" }).click();
  // Step 3 (Review): submit for judgment.
  await page.getByRole("button", { name: /Submit for judgment/ }).click();

  // Lands on the detail page; the verdict banner renders a verdict + confidence.
  await expect(page).toHaveURL(/\/decisions\/.+/);
  await expect(page.getByText("Verdict", { exact: true })).toBeVisible();
  await expect(page.getByText("Confidence", { exact: true })).toBeVisible();
});
