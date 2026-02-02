# Release Management Guide

This repository uses automated workflows to manage releases and generate changelogs.

## Available Release Methods

### Method 1: Draft Releases (Recommended) 🌟

The **Release Drafter** workflow automatically creates and maintains a draft release as you work.

**How it works:**
1. Merge PRs to the `main` or `master` branch
2. The workflow automatically updates a draft release with:
   - Categorized changelog entries
   - Links to PRs and contributors
   - Auto-incremented version number

**Using labels for better changelogs:**
- `feature` or `enhancement` → 🚀 Features section
- `fix`, `bugfix`, or `bug` → 🐛 Bug Fixes section
- `chore` or `dependencies` → 🧰 Maintenance section
- `documentation` or `docs` → 📝 Documentation section

**Version control:**
- `major` label → Bumps X.0.0 (breaking changes)
- `minor` label → Bumps 0.X.0 (new features)
- `patch` label → Bumps 0.0.X (bug fixes)
- Default: patch bump

**To publish a release:**
1. Go to the [Releases page](../../releases)
2. Find the draft release
3. Review the changelog
4. Click "Publish release"

### Method 2: Manual Release Creation

The **Create Release** workflow allows you to create a complete release with one click.

**Steps:**
1. Go to [Actions](../../actions/workflows/create-release.yml)
2. Click "Run workflow"
3. Fill in the inputs:
   - **Version**: Enter version number (e.g., `1.0.5`)
   - **Prerelease**: Check if this is a pre-release
4. Click "Run workflow"

**What it does automatically:**
- ✅ Updates `manifest.json` version
- ✅ Updates `hacs.json` version
- ✅ Generates changelog from CHANGELOG.md or git commits
- ✅ Updates CHANGELOG.md with new version entry
- ✅ Commits all changes
- ✅ Creates and pushes git tag
- ✅ Creates GitHub release with formatted description

### Method 3: Tag-Based Release (Legacy)

The original **Release** workflow triggers on git tag push.

**Steps:**
```bash
git tag -a v1.0.5 -m "Release v1.0.5"
git push origin v1.0.5
```

This method is kept for backward compatibility.

## Best Practices

### For Regular Development

1. **Use meaningful commit messages:**
   ```
   feat: add new temperature sensor
   fix: resolve connection timeout issue
   docs: update installation instructions
   chore: update dependencies
   ```

2. **Label your PRs appropriately:**
   - Helps categorize changes in the changelog
   - Controls version number increments

3. **Keep CHANGELOG.md updated:**
   - Add entries under `[Unreleased]` section
   - Use the [Keep a Changelog](https://keepachangelog.com/) format

### For Releases

1. **Review the draft release before publishing**
   - Check the changelog is complete
   - Verify the version number
   - Test the integration if possible

2. **Use semantic versioning:**
   - **Major** (X.0.0): Breaking changes
   - **Minor** (0.X.0): New features, backward compatible
   - **Patch** (0.0.X): Bug fixes

3. **For HACS users:**
   - The workflows automatically update version numbers
   - Wait for workflows to complete before announcing

## Workflow Files

- `.github/workflows/release-drafter.yml` - Draft release automation
- `.github/workflows/create-release.yml` - Manual release creation
- `.github/workflows/release.yml` - Tag-based release (legacy)
- `.github/release-drafter.yml` - Release drafter configuration

## Troubleshooting

### Draft release not updating
- Check that PRs are merged to `main` or `master`
- Verify the workflow has proper permissions
- Check Actions tab for workflow runs

### Manual release fails
- Ensure version number format is correct (X.Y.Z)
- Check that the tag doesn't already exist
- Verify you have write permissions

### Version not updated in files
- Check workflow logs in Actions tab
- Verify file paths in workflow are correct
- Ensure proper git permissions

## Examples

### Example PR Label Usage
```
Title: Add support for temperature alerts
Labels: feature, minor
```
Result: Added to 🚀 Features, version bumps 0.X.0

### Example Manual Release
```
Version: 1.0.5
Prerelease: false
```
Result: Creates v1.0.5 release with full changelog

## Need Help?

If you encounter issues with the release workflows:
1. Check the [Actions tab](../../actions) for workflow runs and logs
2. Review this documentation
3. Open an issue if problems persist
