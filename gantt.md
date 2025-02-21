```mermaid
%%{init: {"theme": "default", "themeVariables": {}}}%%
gantt
    title Project Timeline (ggplot style)
    dateFormat  YYYY-MM-DD

    %% Events category with subcategories A and B
    section Events
    A :a1, 2025-03-01, 10d
    B :b1, 2025-04-01, 15d

    %% Holidays, etc. category including federal holidays and fiscal year ends
    section Holidays, etc.
    New Year's Day 2025          :h1, 2025-01-01, 1d
    Martin Luther King Jr. Day 2025 :h2, 2025-01-20, 1d
    Washington's Birthday 2025   :h3, 2025-02-17, 1d
    Memorial Day 2025            :h4, 2025-05-26, 1d
    Independence Day 2025        :h5, 2025-07-04, 1d
    Labor Day 2025               :h6, 2025-09-01, 1d
    Columbus Day 2025            :h7, 2025-10-13, 1d
    Veterans Day 2025            :h8, 2025-11-11, 1d
    Thanksgiving Day 2025        :h9, 2025-11-27, 1d
    Christmas Day 2025           :h10, 2025-12-25, 1d
    End of FY25                :h11, 2025-09-30, 1d
    New Year's Day 2026          :h12, 2026-01-01, 1d
    Martin Luther King Jr. Day 2026 :h13, 2026-01-19, 1d
    Washington's Birthday 2026   :h14, 2026-02-16, 1d
    Memorial Day 2026            :h15, 2026-05-25, 1d
    Independence Day 2026        :h16, 2026-07-04, 1d
    Labor Day 2026               :h17, 2026-09-07, 1d
    Columbus Day 2026            :h18, 2026-10-12, 1d
    Veterans Day 2026            :h19, 2026-11-11, 1d
    Thanksgiving Day 2026        :h20, 2026-11-26, 1d
    Christmas Day 2026           :h21, 2026-12-25, 1d
    End of FY26                :h22, 2026-09-30, 1d

    %% Assign tasks to ggplot style classes
    class a1 ggplotBlue;
    class b1 ggplotOrange;
    class h1,h2,h3,h4,h5,h6,h7,h8,h9,h10,h11 ggplotGreen;
    class h12,h13,h14,h15,h16,h17,h18,h19,h20,h21,h22 ggplotRed;

    %% Define ggplot style classes using ggplot2's default palette
    classDef ggplotBlue fill:#1f77b4,stroke:#333,stroke-width:1px;
    classDef ggplotOrange fill:#ff7f0e,stroke:#333,stroke-width:1px;
    classDef ggplotGreen fill:#2ca02c,stroke:#333,stroke-width:1px;
    classDef ggplotRed fill:#d62728,stroke:#333,stroke-width:1px;
```