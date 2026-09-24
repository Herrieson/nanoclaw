---
name: global_fin_database_query
description: Queries the proprietary corporate financial intelligence database using natural language. Use this tool to find internal fixed exchange rates, fiscal policies, and corporate forecasting metrics.
parameters:
  type: object
  properties:
    query:
      type: string
      description: Your natural language query (e.g., "What are today's exchange rates for EUR, GBP, and JPY to USD?").
  required:
    - query
---
