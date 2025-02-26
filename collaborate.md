<details>

<summary markdown="span">Expand Table of Contents</summary>

[[_TOC_]]

</details>

## Simlab

Welcome to the `Collaborate Project`, the **main project** for the PTO GitLab Group. It is intended to encapsulate all of the work, projects, issues, and initiatives conducted within the lab. It serves both as a central hub for collaboration and as an archive of our iterative growth over time.

In our project, we embrace an iterative and open approach to development. We believe that the best results come from continuous refinement, honest communication, and proactive collaboration. Rather than just raising concerns, we encourage everyone to also suggest improvements and offer viable alternatives. Our discussions lead to concrete actions that drive the project forward and ensure that everyone works together productively.

## Background

The Collaborate Project was born out of a need to streamline communication and enhance collaborative efforts across diverse workstreams within the PTO GitLab Group. With roots in our shared objective of continuous improvement, the project builds on our guiding principles of transparency, accountability, and community-driven innovation.

### Goals

Our main goal is to overhaul our current workflow to create a more seamless, effective, and agile process. By integrating robust issue management, clear role delineations, and iterative planning, we aim to:
- Improve communication and collaboration among team members.
- Enhance efficiency by reducing redundancies and ensuring that tasks are actionable.
- Establish a reliable process that scales with our growing team while maintaining high quality output.

---
Introduction

Upon joining the Simulation Team, I encountered a workplace environment marked by significant chaos and disorganization. This document aims to formalize my observations, experiences, and proposals to transform our team into a more efficient, competent, and collaborative unit.
Current State of the Team

The Simulation Team mirrors many of the chaotic environments I have previously experienced. The prevalent disarray undermines any belief that the team can function effectively despite its organizational shortcomings. The inherent interdependence among team members means that individual progress is directly tied to the collective advancement of the entire team. Currently, the team is engaged in a continuous cycle of "putting out fires," which results in both the team's and each member's stagnation—effectively "treading water."
Lack of Fundamental Skills

A critical issue is the team's collective lack of proficiency with essential tools, such as Makefiles. This deficiency severely hampers our ability to build and manage simulations, rendering the Simulation Team less effective and more prone to inefficiency.
Challenges Faced
Organizational Disarray

The chaotic nature of the workplace prevents sustainable progress. When every team member is solely focused on immediate issues, there is little to no time allocated for strategic development or skill enhancement.
Dependency and Stagnation

The team's progress is contingent upon each member's ability to contribute effectively. However, the current state of constant crisis management leaves little room for personal and collective growth, leading to a state of perpetual stagnation.
Ineffective Tool Utilization

Without a solid understanding of fundamental tools like Makefiles, the team struggles to build and maintain simulations. This lack of basic proficiency sets back our ability to deliver quality work and hampers overall productivity.
Personal Approach and Contributions
Building Foundations

When I joined the team, I found myself, along with my colleagues, in a position where we were merely surviving rather than thriving. Recognizing the need for foundational skills, I focused on learning and implementing essential tools, such as Makefiles, which are crucial for building simulations.
Developing Supportive Tools

Beyond personal skill development, I have actively worked to create and implement tools that facilitate the team's progress. These include:

    Bootleg Libraries: Simplifying access to necessary resources.
    Git Repositories and GitLab Integration: Streamlining version control and collaboration.
    Issues Board and Snippets: Enhancing task management and code reuse.
    Search Engine: Improving information retrieval and accessibility.

These tools are designed to move the team from a primitive state of survival to a more organized and thriving community.
Fostering Communication and Collaboration

I have dedicated time to improving communication within the team and making the workplace environment more supportive. This effort aims to create a sense of camaraderie and collective responsibility, essential for long-term success.
Vision for the Team
From Survival to Renaissance

My vision is to transition the team from a state of constant crisis management to a renaissance-like environment where members can focus on sophisticated projects they are passionate about. This transformation requires building a solid foundation of skills and tools that enable creative and efficient work.
Long-Term Competence and Capability

By encouraging team members to engage deeply with essential tools and processes, we can cultivate a more competent and capable team. This approach ensures that each member contributes meaningfully to the team's progress, fostering a culture of continuous improvement and innovation.
Proposed Actions
Revamping the README as an Orientation Bootcamp

To facilitate the onboarding process and ensure new members quickly become productive, I propose the following steps:

    Rewrite the README: Transform the main Git repository's README into a comprehensive orientation guide.
    Explain Repositories and File Structures: Provide clear explanations of the various repositories and their respective file structures.
    Setup Instructions: Offer detailed instructions on setting up the development environment and necessary tools.
    Reference Academic Resources: Direct new members to our academic PDFs and other educational materials to support their learning journey.

Encouraging Skill Development

Promote a culture where team members view time spent learning tools like Git as valuable training for long-term success. For instance, if a team member encounters issues with the Makefile, they should be encouraged to learn Make, thereby enhancing their problem-solving skills and contributing to the team's overall capability.
Delegating Tool Maintenance

While I will continue to develop and introduce new tools, the goal is to empower team members to take ownership of these tools. By providing instructions and fostering a collaborative environment, team members can maintain and improve the tools without relying solely on me.
Conclusion

The Simulation Team stands at a pivotal moment where strategic changes can lead to significant improvements in efficiency, competence, and overall team morale. By addressing organizational disarray, enhancing fundamental skills, and fostering a collaborative culture, we can transform our team from merely surviving to thriving. Implementing the proposed actions will lay the groundwork for a more sophisticated and proud team, ready to tackle complex challenges with confidence and expertise.
---

#### Go Further

At present, our process lacks true iteration. Our work does not yet reflect the natural cycle of refinement, review, and repeat. We need to swim, rather than tread water—creating a dynamic environment where feedback loops drive faster, smarter improvements. By formalizing an iterative process, we can ensure that our work continuously evolves, staying responsive to emerging insights and challenges.

#### Do More With Less

Even as our team grows, we remain a lean unit compared to industry giants. This means we must be **more efficient**, **more automated**, and **work intelligently**. By leveraging automated processes and streamlining communication channels, we can maximize the impact of our limited resources and deliver high-quality results without unnecessary overhead.

### Roadmap

- [PTO GitLab Roadmap](https://gitlab.com/groupts/PTO/~/roadmap)

## New Users

Welcome to the project! If you’re new here, we recommend that you familiarize yourself with our guidelines, group structures, and the overall workflow documented below.

### Description of Groups, and SubGroups

#### Simulations

The simulation groups are focused on testing and modeling our various environments. They include:

##### PBX

Dedicated to work related to the PBX simulation environment.  
See also: [Additional PBX documentation](#)

##### PBY

Focused on simulation aspects under the PBY umbrella.

#### Other Projects

Other projects within the group may pertain to utility tools, integrations, and specialized research initiatives. Each project follows a similar collaborative and iterative model.

## Work Flow

Our workflow leverages Issues, Milestones, and Epics to manage progress. Every task begins with an issue where we capture ideas, bugs, and requests in detail. With clear labels, time estimates, and structured branching, our process ensures that no detail is overlooked. Discussion and action go hand in hand, and through regular updates and sprint reviews, we keep our workflow both responsive and transparent.

### Issues

Issues are the fundamental units of our project management process. They capture bug reports, feature requests, tasks, and everything in between that the team needs to address.

#### When to create an issue?

Before creating an issue, ask yourself the following questions:

- Does this affect anyone but me?
- Is it actionable?
- Should the team be aware?
- Is it meaningful?
- Does it involve the LAN, or something on the LAN?

Below is a flowchart that illustrates this decision process:

```
flowchart TD
    A[Start] --> B{Does this affect anyone besides you?}
    B -- No --> C[No need to create an issue – fix it privately]
    B -- Yes --> D{Is the issue actionable?}
    D -- No --> E[Gather more details / clarify the problem before proceeding]
    D -- Yes --> F{Should the team be aware of this?}
    F -- No --> G[Address the issue informally (e.g., via chat) or document for future reference]
    F -- Yes --> H{Is the impact meaningful?}
    H -- No --> I[Not critical – consider discussing it in team meetings rather than an issue]
    H -- Yes --> J{Does it involve the LAN or core infrastructure?}
    J -- Yes --> K[Create an issue on GitLab immediately]
    J -- No --> L[Create an issue and consider if it requires additional context or discussion]
    K --> M[Follow up with team communication and updates]
    L --> M
```

#### Labels

Each issue can have several labels that help classify and prioritize the work. Labels may be nested and combined to form a complete picture of the issue status. Use the table below as a reference for our core labels.

Below is a table outlining all our defined labels:

| Label Category | Label            | Sub-Label (if any)  | Description                                                      | When to Use                                        | Requires Issue Branch? |
|----------------|------------------|---------------------|------------------------------------------------------------------|----------------------------------------------------|------------------------|
| Type           | Bug              | (None)              | A bug that needs fixing                                          | When an unexpected behavior affects functionality  | No                     |
| Type           | Task             | (None)              | A task requiring modifications, enhancements, or additions       | When a clear deliverable is identified             | Yes                    |
| Type           | Discussion       | (None)              | An issue for open discussion or brainstorming                    | When gathering perspectives or debating ideas      | No                     |
| Type           | Study            | (None)              | Requires research or investigation into a particular subject     | When a study is being performed                    | Yes                    |
| Type           | Proposal         | (None)              | Contains proposals for new features or process changes           | When suggesting new approaches or changes          | No                     |
| Type           | Software Request | (None)              | A request related to new software installations or modifications | When new software setups or updates are needed     | No                     |
| Type           | Question         | (None)              | Queries looking for clarification or additional detail           | When a question or ambiguous situation arises      | No                     |
| Type           | Task             | Write Documentation | Denotes tasks related to creating or updating documentation      | When documentation needs to be prepared or refined | Yes                    |
| Type           | Task             | Code Implementation | Denotes tasks related to code writing or modification            | When a code-based solution is required             | Yes                    |

##### Top Level Labels

Below are more label categories that help further refine issue classification.

The top level labels are:

- [Event](#event-labels)
- [Stage](#stage-labels)
- [Priority](#priority-labels)
- [Simulation](#simulation-labels)
- [Team](#team-labels)
- [Type](#type-labels-additional-details)

###### Event Labels

| Label    | Description                                           |
|----------|-------------------------------------------------------|
| Event::A | Indicates the occurrence of a significant event A     |
| Event::B | Denotes an important event B that may impact workflow |

###### Stage Labels

| Label                      | Description                                                  |
|----------------------------|--------------------------------------------------------------|
| Stage::Abandoned           | The task has been abandoned                                  |
| Stage::Backlog             | The task is in backlog and not yet prioritized               |
| Stage::Completed           | The task has been completed                                  |
| Stage::In Progress         | The task is currently being worked on                        |
| Stage::In Progress::Draft  | The work is developing in a preliminary draft stage          |
| Stage::In Progress::Review | The work is completed and under review                       |
| Stage::Pending Approval    | Work is finished and awaiting final approval                 |
| Stage::Unresolved          | The issue remains unresolved and requires further discussion |
| Stage::Zombie              | Work appears stalled or abandoned, lacking active progress   |

###### Priority Labels

Below is our table of priority levels and their meanings:

| Priority Label | Meaning                                                                   |
|----------------|---------------------------------------------------------------------------|
| Priority::A    | Critical – must be addressed immediately; often blocking further progress |
| Priority::B    | High – important and should be resolved soon                              |
| Priority::C    | Medium – requires attention but can be scheduled for later                |
| Priority::D    | Low – minimal impact, can be addressed in due course                      |
| Priority::E    | Trivial – minor, cosmetic, or optional issues                             |

###### Simulation Labels

| Label                 | Description                                                           |
|-----------------------|-----------------------------------------------------------------------|
| Simulation::PBX       | Issues related to the PBX simulation environment                      |
| Simulation::PBY       | Issues related to the PBY simulation aspects                          |

###### Team Labels

| Label   | Description                                          |
|---------|------------------------------------------------------|
| Team::A | Assigned primarily to Team A’s scope                 |
| Team::B | Associated with issues under Team B’s responsibility |
| Team::C | Related to tasks managed within Team C               |

###### Type Labels (Additional Details)

| Label                  | Sub-Label                   | Description                                                      |
|------------------------|-----------------------------|------------------------------------------------------------------|
| Type::Bug              | (None)                      | Indicates an error or malfunction needing resolution             |
| Type::Bug              | Team::A / Team::B / Team::C | Specifies a bug affecting a particular team element              |
| Type::Discussion       | (None)                      | Marks an issue intended for open discussion or brainstorming     |
| Type::Study            | (None)                      | Requires additional research or technical analysis               |
| Type::Proposal         | (None)                      | Contains suggestions or proposals for significant changes        |
| Type::Software Request | (None)                      | A request for new software installations or modifications        |
| Type::Question         | (None)                      | An inquiry intended to solicit further details or clarifications |
| Type::Task             | Write Documentation         | Denotes documentation-related work                               |
| Type::Task             | Code Implementation         | Denotes coding or development-related tasks                      |

#### Weights

Every issue is assigned three key attributes: the estimated time, the weight, and, once completed, the actual time spent. The weight reflects the level of uncertainty based on complexity, effort, and doubt.

We use a relative sizing approach, often modeled on a Fibonacci-like sequence, with suggested weights of 1, 2, 3, 5, 8, and 13:

| Weight | Indication                                                                             |
|--------|----------------------------------------------------------------------------------------|
| 1      | Minimal uncertainty; trivial task with very little complexity, effort, or doubt        |
| 2      | Low uncertainty; simple task with minimal challenges                                   |
| 3      | Moderate uncertainty; task with a fair level of complexity or effort                   |
| 5      | Higher uncertainty; task requiring significant work and involving some unknowns        |
| 8      | Significant uncertainty; task with high complexity or several unknown factors          |
| 13     | Very high uncertainty; large and complex task with significant risks and uncertainties |

Weights and time estimates are assigned before work begins to ensure a shared understanding of the task’s scope.

#### Creating Time Estimates

When a new issue is created in GitLab, we set a time estimate using a shortcut command. For example:

/estimate 4h

This sets the expected time to complete the issue. The weight is documented either in the issue description or in our project tracking tool.

#### Recording Actual Time

Once work is completed, update the issue with the actual time spent using:

/spent 3h

Keeping these records helps compare initial estimates with actual time taken, which in turn informs future planning and resource allocation.

### Branches

Sometimes, issues require that a branch be created so that work can be isolated for easier testing, code reviews, and integration. Always link your branch to the corresponding issue and follow the naming conventions outlined in our branch guidelines.

### Sprints

Our sprints begin at 1300 on Monday of long weeks and conclude at 1400 on Working Fridays. This cadence helps maintain a rhythm of regular progress and timely reviews.

### Help

#### Markdown

For a complete guide on Markdown, please see our internal guide: [Markdown Guide](.internal/markdown.md).  
Also, check out the official GitLab Markdown documentation for more details: [GitLab Markdown Help](https://docs.gitlab.com/ee/user/markdown.html)

#### Q&A

##### What is Git?

Git is a distributed version control system that allows multiple developers to work on a project simultaneously. It tracks changes in source code (**or any files**), facilitates collaboration through branching and merging, and helps maintain a full history of project changes, ensuring that contributions are integrated smoothly and reliably.

##### What is GitLab?

GitLab is a web-based DevOps lifecycle tool that provides a platform for managing Git repositories, continuous integration/continuous deployment (CI/CD), issue tracking, and project management all in one place. It fosters collaboration across teams and streamlines the development process, from planning through deployment.

#### Helpful Links

Here are some useful links to GitLab documentation and related resources:

- [GitLab Docs Home](https://docs.gitlab.com/)
- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
- [GitLab Issue Boards](https://docs.gitlab.com/ee/user/project/issue_boards.html)
- [GitLab Merge Requests](https://docs.gitlab.com/ee/user/project/merge_requests/)
- [GitLab Web IDE](https://docs.gitlab.com/ee/user/project/web_ide.html)
- [GitLab API Documentation](https://docs.gitlab.com/ee/api/)
- [GitLab Security Documentation](https://docs.gitlab.com/ee/user/application_security/)
- [GitLab Runner Documentation](https://docs.gitlab.com/runner/)
