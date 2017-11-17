# Save FIW

This is a tool for scraping forum posts from an InvisionFree board.
The tool will gather as much data as it can from each topic
and save them as JSON files.

## Requirements

* [Python 3.x](https://python.org)

## Parameters

*   `urlTemplate`: the URL representing a topic on the target forum.
*   `start`: the first Topic ID to scrape
*   `stop`: the last Topic ID to scrape.
    Should be greater than or equal to `start`.
*   `outputFolder`: the folder where data files will be saved.

## Procedure

The script visits the given `urlTemplate`
using Topic IDs ranging from the given `start` to the given `stop`.
Currently this is configured at the top of `scrape.py`.

For each topic ID, the `urlTemplate` replaces the `{}` token with the topic ID.

The script gathers the topic title and subtitle.
Then it collects all posts it can see on that topic
and stores them as "entries".

Each entry contains the entry ID, the author's numeric ID (or null for guests),
the user name of the author, the date (currently in a not-so-computer-friendly
format), and the generated HTML of the post message.

The script will navigate through pages of the thread
until it finds no more pages to visit.
Then it will proceed to the next thread ID.

For each topic where at least one post is found,
a JSON file is saved to `outputFolder`.
