Below is an example of how we define our workflow for issue management in our README.md. We assign three key attributes to every issue: the estimated time, the weight, and, once completed, the actual time. We create the time estimate and weight when the issue is opened—before we record the actual time spent.

Weight is our measure of uncertainty. It factors in the following:
	•	Complexity: What needs to be figured out.
	•	Effort: The sheer amount of work required.
	•	Doubt: The unknowns or risks that might affect the work.

Using a relative sizing approach (often based on a Fibonacci sequence), we choose weights from 1, 2, 3, 5, 8, and 13. A longer task might indicate a higher weight due to the inherent uncertainty—even if the work is straightforward (which is rare). The final point estimate lets us say, “taking all factors into account, this task is bigger than a 3 and smaller than an 8, so we assign it a 5.”

Workflow

Issue Weight

We use the following table as a guideline for our issue weights:

Weight	Indication
1	Minimal uncertainty; trivial tasks with very little complexity, effort, or doubt.
2	Low uncertainty; small tasks that are straightforward with minor unknowns.
3	Moderate uncertainty; tasks with a fair amount of complexity or effort.
5	Higher uncertainty; tasks that involve a mix of non-trivial complexity, effort, and some doubt.
8	Significant uncertainty; tasks with high complexity or multiple unknown factors.
13	Very high uncertainty; tasks that are large, complex, and fraught with doubts or risks.

The weight is assigned at the same time as the estimated time, providing an early indicator of potential risks or challenges in the issue.

Creating Time Estimates

When we create a new issue in GitLab, we set a time estimate along with its weight. This is done before any work is started, so we have a clear plan. For example, we use the GitLab shortcut:

/estimate 4h

This command sets the estimated time for the issue. We record the weight in the issue description or in our project management tool alongside the time estimate.

Recording Actual Time

Once the work is completed, we update the issue with the actual time spent. We use the GitLab shortcut for logging work:

/spent 3h

This command records the actual time taken, allowing us to later compare our estimates with reality. Over time, these comparisons help us fine-tune our estimations and weight assignments.

By consistently applying these practices, we ensure that every issue is well-understood from the start and that our time-tracking remains both transparent and accountable.