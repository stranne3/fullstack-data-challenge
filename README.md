## Scatterplot Data Challenge

This exercise evaluates your ability to build a small full-stack application.  
A SQLite database (`db.sqlite`) is included in the repository and contains a set of test data points together with hourly
values for each point. Your task is to create a backend and a frontend that together present this data in a clear and
meaningful way.

### Background

The dataset consists of:
- A set of named points, each placed on a normalized coordinate system (x/y between 0 and 1).
- A collection of time-series measurements connected to each point. The data spans roughly one month with one
  measurement every hour.

Your goal is to design a solution that lets a user explore this data visually. You decide how to present the information
and which insights should be highlighted, as long as the output is easy to understand and adds value.

### Setup

1. Clone the repository.
2. Inspect the included `db.sqlite` file to understand the schema and data.
3. Use any stack you prefer to implement a backend that exposes the data in a suitable format.
4. Build a frontend that consumes this backend and visualizes the data.

No containers or external services are required. The only dependency is the SQLite file in the repository.

### Requirements

1. **Backend**
    - Provide an API that exposes the data in whatever format best suits your frontend.
    - Use any framework, language, or architecture.
    - Add any endpoints you find helpful. You may also add extra functionality, such as CRUD operations, if you think it
      improves the overall solution or showcases your skills.

2. **Frontend**
    - Visualize the dataset in a way that makes relationships and patterns clear:
        - scatterplots, time-series charts, heatmaps, dashboards. Choose whatever works best.
    - Any web framework or visualization library is allowed.
    - Focus on presenting the data in a way that’s easy to interpret.

3. **General**
    - You may overengineer the solution if you want, just be prepared to explain your design decisions.
    - Extra features are welcome, whether they add insight, improve the UX, or demonstrate architectural thinking.
    - Keep performance in mind. The time-series data is relatively large and should be handled efficiently.
    - You may preprocess or reshape the data in the backend as needed.

### Guidelines

- The task should be completable within a few hours, but you may take as much time as you need.
- You are free to use any tools, libraries, or languages.
- You may use AI tools to assist you, but ensure you understand the implementation.
- Be ready to discuss your approach, trade-offs, and any additional features you chose to include.

### Delivery

- Submit your solution as a zipped project.
- Include any instructions or scripts needed to run your backend and frontend.
- A review meeting will be scheduled where we walk through the solution and discuss your choices.

**Have fun and good luck!**
