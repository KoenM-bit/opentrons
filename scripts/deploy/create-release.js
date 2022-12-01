'use strict'

// Creates a release asset in github for a tag with autogenerated changelogs following
// conventional-commit specifications.
//
// Usage: node create-release.js <token> <tag> [--deploy]
// token should be a github token capable of creating a release
// tag should be the tag for which the release should be created
// --deploy should be specified to actually create the release; if not specified, the script
//          will print what it would do but not do it
// --allow-old allows the use of a tag that does not point to one of the last 100 commits. We
//             only check the last 100 commits for the recent tag to not bog everything down,
//             so normally if you try to make a release for a really old commit the check that
//             prevents you from getting a conventional-changelog for the wrong thing will
//             false-positive. Set this flag to not do that check.
// The release will be created as a prerelease if this is a prerelease tag.
// It will always be created as a draft so that humans can review it before it goes live.
//
// The changelog content will be in the body of the release.

const parseArgs = require('./lib/parseArgs')
const conventionalChangelog = require('conventional-changelog')
const git = require('simple-git')
const semver = require('semver')
const { Octokit } = require('@octokit/rest')
const ALLOWED_VERSION_TYPES = ['alpha', 'beta', 'candidate', 'production']
const USAGE = '\nUsage:\n node ./scripts/deploy/create-release <token> <tag> [--deploy] [--allow-old]'

const REPO_DETAILS = {
  owner: 'Opentrons',
  repo: 'opentrons'
}

const detailsFromTag = (tag) => tag.includes('@') ? tag.split('@') : ['robot-stack', tag.substring(1)]
function tagFromDetails(project, version) {
  if (project === 'robot-stack') {
    return 'v' + version
  } else {
    return [project, version].join('@')
  }
}
function prefixForProject(project) {
  if (project === 'robot-stack') {
    return 'v'
  } else {
    return project + '@'
  }
}

const releaseKind = version => (semver.prerelease(version)?.at(0) ?? 'production').split('-')[0]
const releasePriorityGEQ = (kindA, kindB) => ALLOWED_VERSION_TYPES.indexOf(kindA) >= ALLOWED_VERSION_TYPES.indexOf(kindB)

// Return the version to build a changelog from, which is the most recent version whose prerelease
// level is equal to or greater than the current tag. So
// - if currentVersion is a production version (no prerelease data), use the last production version
// - if currentVersion is a beta version, use the most recent version that is either beta or production
// - if currentVersion is an alpha version, use the most recent version of any kind
// currentVersion should be the version-part of the tag (i.e. not including project@, not including v)
// previousVersions should be an array of version-parts (see above) in descending semver order
function versionPrevious(currentVersion, previousVersions) {
  const currentReleaseKind = releaseKind(currentVersion)
  if (!ALLOWED_VERSION_TYPES.includes(currentReleaseKind)) {
    throw new Error(`Error: Prerelease tag ${currentReleaseKind} is not one of ${ALLOWED_VERSION_TYPES.join(', ')}`)
  }
  const from = previousVersions.indexOf(currentVersion)
  const notIncluding = previousVersions.slice(from+1)
  const releasesOfGEQKind = notIncluding.filter(
    version => releasePriorityGEQ(releaseKind(version), currentReleaseKind)
  )
  return releasesOfGEQKind.length === 0 ? null : releasesOfGEQKind[0]
}

const titleForRelease = (project, version) => `${project.replaceAll('-', ' ')} version ${version}`

async function createRelease(token, tag, project, version, changelog, deploy) {
  const title = titleForRelease(project, version)
  const isPre = !!semver.prerelease(version)
  if (deploy) {
    const octokit = new Octokit({
      auth: token,
      userAgent: 'Opentrons Release Creator'
    })
    await octokit.reset.createRelease({
      owner: REPO_DETAILS.owner,
      repo: REPO_DETAILS.repo,
      tag_name: tag,
      name: title,
      body: changelog,
      draft: true,
      prerelease: isPre
    })
  } else {
    console.log(`${tag} ${title}\n${changelog}\n${isPre ? '\nprerelease' : ''}`)
  }
}

async function main() {
  const { args, flags } = parseArgs(process.argv.slice(2))

  const [token, tag] = args
  if (!token || !tag) {
    throw new Error(USAGE)
  }

  const deploy = flags.includes('--deploy')
  const allowOld = flags.includes('--allow-old')

  if (!allowOld) {
    const last100 = await git().log({from: 'HEAD~100', to: 'HEAD'})
    if (!last100.all.some(commit => commit.refs.includes('tag: ' + tag))) {
      throw new Error(
        `Cannot find tag ${tag} in last 100 commits. You must run this script from a ref with ` +
        `the tag in its history to correctly generate a changelog. If your tag is very old but ` +
        `is definitely in whatever branch is checked out, use --allow-old.`)
    }
  }

  const [project, currentVersion] = detailsFromTag(tag)

  console.log(`Tag ${tag} represents version ${currentVersion} of ${project}`)

  const allTags = (await git().tags([prefixForProject(project) + '*'])).all
  if (!allTags.includes(tag)) {
    throw new Error(`Tag ${tag} does not exist - create it before running this script`)
  }
  const sortedVersions = allTags.map(tag => detailsFromTag(tag)[1]).sort(semver.compare).reverse()

  const previousVersion = versionPrevious(currentVersion, sortedVersions)
  const previousTag = tagFromDetails(project, previousVersion)

  const changelogStream = conventionalChangelog(
    {preset: 'angular', tagPrefix: prefixForProject(project)},
    {gitSemverTags: allTags,
     version: currentVersion,
     currentTag: tag,
     previousTag: previousTag,
     host: 'https://github.com',
     owner: REPO_DETAILS.owner,
     repository: REPO_DETAILS.repo,
     linkReferences: true
    },
    {from: previousTag}
  )
  const chunks = []
  for await (const chunk of changelogStream) {
    chunks.push(chunk.toString())
  }
  // For some reason, later chunks include the contents of earlier chunks so we need to
  // accumulate chunks in reverse and drop earlier chunks that are included in later ones
  const changelog = chunks.reverse().reduce(
    (accum, chunk) => accum.includes(chunk.trim()) ? accum : chunk + accum, '')
  await createRelease(token, tag, project, currentVersion, changelog, deploy)
}

(async () => {
  try {
    await main()
  } catch (err) {
    console.error('Release failed: ', err)
    process.exit(-1)
  }
})()
