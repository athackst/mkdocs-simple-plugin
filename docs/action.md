# GitHub Action

## Enable GitHub pages

First, set up your github repository to enable gh-pages support.

See [Github Pages](https://pages.github.com/) for more information.

## Deploy from GitHub Actions

Create a yaml file with the following contents in the `.github/workflows` directory in your repository

```yaml
jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v2
      - name: Build docs
        uses: athackst/mkdocs-simple-plugin
        with:
          publish_branch: gh-pages # optionally specify branch
        env:
          # Optional environment parameters for mkdocs.yml generation
          REPO_URL: https://github.com/${{ github.repository }} # The URL of the repository the docs should point to
          SITE_NAME: ${{ github.repository }} # The name of the site
          SITE_URL: https://{{ github.repository_owner }}.github.io/${{ github.event.repository.name }} # The URL of the site
```
