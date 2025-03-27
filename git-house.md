"""
gitGraph
   commit id: "Init"
   branch contractor
   commit id: "Contractor Commit 1"
   commit id: "Contractor Commit 2"
   tag "Version-15"  // Tag on an earlier commit, behind the head
   commit id: "Contractor Commit 3" tag: "input-refactor"
   commit id: "Contractor Commit 4" tag: "bug-fix"
   branch main from contractor
   checkout main
   commit id: "Main Commit 1"
   commit id: "Main Commit 2"
   merge contractor id: "Monthly Merge" // Every month, contractor is merged into main
   commit id: "Main Commit 3"
   checkout contractor
   commit id: "Contractor Commit 5" tag: "input-refactor"
   commit id: "Contractor Commit 6" tag: "bug-fix"
   checkout main
   merge contractor id: "Monthly Merge 2"
"""


---
Imagine your house was built decades ago and labeled as “Version 15”—a perfect snapshot of how it looked back then. Now, you’ve seen a couple of exciting new features, like a state-of-the-art gourmet kitchen and a luxury swimming pool, that you really want in your home. However, these features depend on a series of modern upgrades such as improved plumbing, electrical systems, and reinforced foundations. They’re not just cosmetic add-ons; they need the whole house to be updated.

If you insist on sticking with your old “Version 15” house, you’d be trying to add these new features on top of an outdated structure. You might attempt to cherry-pick just the kitchen and pool designs, but without the necessary foundational changes made between then and now, these features won’t function properly—or might even cause more problems.

In Git terms, “Version 15” is a fixed tag—a snapshot of the project at one moment. It doesn’t evolve or incorporate later changes. The main branch, on the other hand, is like the modern, updated version of your house. It includes all the incremental improvements and necessary changes that support the new features. So, rather than forcing your old house to adopt these modern upgrades, it makes much more sense to use the main branch where all those changes are already in place.


---

Imagine your old house as a fixed snapshot from decades ago—let’s call it “Version 15.” Now, you see some amazing new features, like a gourmet kitchen and a luxury swimming pool, that you really want. However, these features aren’t just standalone upgrades; they depend on a whole series of modern improvements—like updated plumbing, electrical work, and a stronger foundation. If you try to add these features to your old “Version 15” house without those underlying upgrades, things just won’t work right.

Now, here’s where the jargon can get annoying. Terms like “drop,” “snapshot,” “release,” and “build” are all fancy words that often mean the same thing—a tag. In Git, a tag is simply a label that marks a specific point in your project’s history, much like that photo of your house in its “Version 15” state. When people talk about releasing a build or dropping a new version, they’re usually referring to tagging the code at a particular point.

So, if you’re stuck on “Version 15” (that fixed tag), you’re not getting the benefits of all the modern improvements—just like trying to add a gourmet kitchen to an outdated house without the necessary renovations. Instead, using the main branch (your continuously updated, modern home) means you’re already set up with all the upgrades that support those coveted new features.


---

"""
import sys
import git

def generate_mermaid(repo_path):
    # Open the repository
    repo = git.Repo(repo_path)
    
    # Start building the Mermaid diagram
    mermaid_lines = ["```mermaid", "gitGraph"]
    
    # Get the list of local branches
    branches = repo.branches
    
    # For demonstration, we’ll iterate over each branch
    for branch in branches:
        mermaid_lines.append(f"   branch {branch.name}")
        # Get all commits for the branch, earliest first
        commits = list(repo.iter_commits(branch.name))
        commits.reverse()
        for commit in commits:
            # Use a short commit hash and the first line of the commit message
            short_sha = commit.hexsha[:7]
            message = commit.message.splitlines()[0].replace('"', "'")
            mermaid_lines.append(f"   commit id: \"{short_sha}\" message: \"{message}\"")
    
    mermaid_lines.append("```")
    return "\n".join(mermaid_lines)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python git_to_mermaid.py /path/to/git/repo")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    diagram = generate_mermaid(repo_path)
    print(diagram)
"""