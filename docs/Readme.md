## Todos

- TODO: more manual testing of react async edge cases 
    -  in particular, webcam didn't always turn off when closing session? but I may have fixed that bug already
- TODO: add run instructions for mac, windows, linux, including system dependencies (within reason)
- TODO: do cross-platform testing (Windows, Ubuntu VM)
- TODO: do cross-browser testing (Safari, Chrome)
- TODO: test concurrent users better
- TODO: test when multiple webcams are available
- TODO: add some automated pytests (sequenced REST calls?)
- TODO: look into how React apps are packaged -- can we do better? 
- TODO: how to parametrize host info in react app? 
- TODO: basic CI pipeline with github actions?
- TODO: cut a release
- TODO: clean up dead code (like the docker stuff)
- TODO: cleanup requirements.txt cruft (overly specific -> dependency hell)
- TODO: Provide way to get all the smiles from DB

- TODO: Document some of the invariants and inferred requirements that led to certain design decisions
  - Principles
    - Principle 1A: The app should be able to handle a modest number of concurrent connections without excessive contention on the single webcam. 
    - Principle 1B: The backend should support multiple worker processes.
    - Principle 2: These concurrent connections would all come from localhost only, for now. It isn't production code. 
    - Principle 3: The application should run locally on my old Intel Mac without trouble. 
    - Principle 4: The number of dependencies and services should be minimized, to avoid complex cross-platform configuration.
    - Principle 5: Design should be modular enough to allow modification in the future. 
    - Principle 6: Use tech I'm most familiar with when it makes sense to
  - Example implications
    - Chose to use flask because I'd used it a lot in the past, even though fastapi is arguably better suited to this problem in hindsight.
    - This DIY DB-based session management... I certainly didn't set out to do this on purpose from the beginning. It happened organically. 
        - Principle 1 wasn't immediately apparent to me when I was just messing around with tkinter and getting the python piece working. Then I had multiple browser tabs of the app, and had to be able to start and stop the feed at will... the need to keep track of state became very apparent then. 
        - Principle 1B + 4 necessitated using the filesystem for synchronization.

