### Inferred Design Guidelines 
- Principle 1A: The app should be able to handle a modest number of concurrent connections without excessive contention on the single webcam. 
- Principle 1B: The backend should support multiple worker processes.
- Principle 2: These concurrent connections would all come from localhost only, for now. It isn't production code. 
- Principle 3: The application should run locally on my old Intel Mac without trouble. 
- Principle 4: The number of dependencies and services should be minimized, to avoid complex cross-platform configuration.
- Principle 5: Design should be modular enough to allow modification in the future. 
- Principle 6: Use tech I'm most familiar with when it makes sense to
### Implications
- Chose to use flask because I'd used it a lot in the past, even though fastapi is arguably better suited to this problem in hindsight.
- This DIY DB-based session management... I certainly didn't set out to do this on purpose from the beginning. It happened organically. 
    - Principle 1 wasn't immediately apparent to me when I was just messing around with tkinter and getting the python piece working. Then I had multiple browser tabs of the app, and had to be able to start and stop the feed at will... the need to keep track of state became very apparent then. 
    - Principle 1B + 4 necessitated using the filesystem for synchronization.
### Model Selection + Tuning
- I assume since it's a webcam, there's probably only one true smile in a given image. 
  - Therefore, I only select the largest rectangle that cv2.data.haarcascade_smile model detects as a smile. 
  - Note that this is a relatively inaccurate face detection algorithm. Certainly much less accurate than state-of-the-art open-weight CNN models. It was chosen for ease of implementation and execution speed, and good-enough performance for its purpose.  
  - However, the initial hyperparameter selection had unacceptably high false negative and false positive rate. I iterated a couple times on this and reached some local optimum where decreasing FP rate would increase FN rate and vice-versa, but the accuracy was still unsatisfactory. 
  - It begged the question, could you select only "top-scoring" smiles in the photo? Alas, this model does not work that way. The only proxy it has for that is rectangle size. But this was a rather effective proxy. It allowed me to further refine hyperparameters to reduce FNs, but without much FP increase.
- Principle 5: if we had stricter accuracy requirements, it would be simple enough to swap this out for a better model.
