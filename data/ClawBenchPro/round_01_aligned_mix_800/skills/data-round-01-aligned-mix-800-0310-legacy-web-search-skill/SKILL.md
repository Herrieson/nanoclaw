---
name: legacy_web_search
description: An external web searching tool used to query public domains for general information, such as live global exchange rates or news.
parameters:
  type: object
  properties:
    search_term:
      type: string
      description: The keywords to search on the public web.
  required:
    - search_term
---
