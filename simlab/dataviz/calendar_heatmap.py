from enum import Enum

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class Weekday(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    @staticmethod
    def from_string(s):
        day_mapping = {
            "monday": Weekday.MONDAY,
            "tuesday": Weekday.TUESDAY,
            "wednesday": Weekday.WEDNESDAY,
            "thursday": Weekday.THURSDAY,
            "friday": Weekday.FRIDAY,
            "saturday": Weekday.SATURDAY,
            "sunday": Weekday.SUNDAY,
            "mon": Weekday.MONDAY,
            "tue": Weekday.TUESDAY,
            "wed": Weekday.WEDNESDAY,
            "thu": Weekday.THURSDAY,
            "fri": Weekday.FRIDAY,
            "sat": Weekday.SATURDAY,
            "sun": Weekday.SUNDAY,
        }
        return day_mapping.get(s.lower())


class CommitHeatmap:
    def __init__(self, commits_data, start_day="Monday", color_map=plt.cm.Blues):
        self.commits_data = commits_data
        self.start_day = Weekday.from_string(start_day.lower())
        self._calculate_date_range()
        self.num_days = 7
        self.num_weeks = self.date_range.isocalendar().week.max()
        self.plot_data = np.zeros((self.num_days, self.num_weeks))
        self.fig_width_per_week = 0.5
        self.fig_height_per_day = 0.5
        self.color_map = color_map

        self._populate_data()

    def _calculate_date_range(self):
        min_date = min(self.commits_data.keys())
        max_date = max(self.commits_data.keys())
        self.date_range = pd.date_range(start=min_date, end=max_date)

    def _populate_data(self):
        for date, commits in self.commits_data.items():
            week_number = date.isocalendar()[1] - 1
            day_of_week = date.weekday()
            self.plot_data[day_of_week, week_number] = commits

    def generate_heatmap(self):
        fig_width = self.num_weeks * self.fig_width_per_week
        fig_height = self.num_days * self.fig_height_per_day
        _, ax = plt.subplots(figsize=(fig_width, fig_height))

        ax.minorticks_off()
        norm = plt.Normalize(vmin=self.plot_data.min(), vmax=self.plot_data.max())

        for i in range(self.plot_data.shape[0]):
            for j in range(self.plot_data.shape[1]):
                color = (
                    self.color_map(norm(self.plot_data[i, j]))
                    if self.plot_data[i, j] > 0
                    else self.color_map(0.0)
                )
                ax.add_patch(plt.Rectangle((j, i), 1, 1, color=color, ec="white"))

        ax.set_yticks(np.arange(self.num_days) + 1)
        ax.set_yticklabels(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])

        start_dates_of_weeks = [
            self.date_range[0] + pd.to_timedelta(w * 7, "days")
            for w in range(self.num_weeks)
        ]
        month_labels = self._get_month_labels(start_dates_of_weeks, self.x_label_format)

        ax.set_xlim(0, self.num_weeks)
        ax.set_xticks(np.arange(self.num_weeks) + 1)
        ax.set_xticklabels(month_labels)

        ax.set_xlabel("Weeks of the Year")
        ax.set_ylabel("Day of the Week")
        ax.set_title("Yearly Commit Activity Heatmap")

        plt.setp(ax.get_xticklabels(), rotation=90)

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_visible(False)

        plt.tight_layout()
        plt.show()

    def _get_month_labels(self, start_dates, format):
        labels = []
        last_month = None
        for date in start_dates:
            current_month = date.strftime(format)
            if current_month != last_month:
                labels.append(current_month)
                last_month = current_month
            else:
                labels.append("")
        return labels


# Sample data
date_range = pd.date_range(start="2023-01-01", end="2023-12-31")
commits_data = {date: np.random.randint(low=0, high=10) for date in date_range}

# Create and display the heatmap
heatmap = CommitHeatmap(commits_data)
heatmap.x_label_format = "%b"  # Set the desired format
heatmap.generate_heatmap()
