# Publish this repository on GitHub

No editor email is needed for this step.

1. Create a new **public** repository named `trojans-aerofleetx`.
2. Do not initialise it with another README, `.gitignore`, or licence.
3. Open a terminal in this repository and run:

```bash
git remote add origin https://github.com/YOUR_USERNAME/trojans-aerofleetx.git
git branch -M main
git push -u origin main
```

4. Open the GitHub **Actions** tab and select **Android clean build and tests**.
5. Run the workflow, or let the push start it automatically.
6. When it is green, copy the run link and commit SHA into `docs/BUILD_VERIFICATION.md`.
7. Replace `TO_BE_ADDED_AFTER_GITHUB_PUBLICATION` in `CITATION.cff` with the repository URL.
8. Create a tag such as `v1.3.0-rc2`, then archive the tagged release on Zenodo as software.
9. Never commit a keystore, password, signing certificate private key, or `keystore.properties`.
