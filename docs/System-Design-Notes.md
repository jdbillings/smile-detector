### Inferred Design Guidelines 
- Principle 1A: The app should be able to handle a modest number of concurrent connections without excessive contention on the single webcam. 
- Principle 1B: The backend should support multiple worker processes.
- Principle 2: These concurrent connections would all come from localhost only, for now. It isn't production code. 
- Principle 3: The application should run locally on my old Intel Mac without trouble. 
- Principle 4: The number of dependencies and services should be minimized, to avoid complex cross-platform configuration.
- Principle 5: Design should be modular enough to allow modification in the future. 
- Principle 6: Use tech I'm most familiar with when it makes sense to

### Model Selection + Tuning
- I assume since it's a webcam, there's probably only one true smile in a given image. 
  - Therefore, I only select the largest rectangle that cv2.data.haarcascade_smile model detects as a smile. 
  - Note that this is a relatively inaccurate face detection algorithm. Certainly much less accurate than state-of-the-art open-weight CNN models. It was chosen for ease of implementation and execution speed, and good-enough performance for its purpose.  
  - However, the initial hyperparameter selection had unacceptably high false negative and false positive rate. I iterated a couple times on this and reached some local optimum where decreasing FP rate would increase FN rate and vice-versa, but the accuracy was still unsatisfactory. 
  - It begged the question, could you select only "top-scoring" smiles in the photo? Alas, this model does not work that way. The only proxy it has for that is rectangle size. But this was a rather effective proxy. It allowed me to further refine hyperparameters to reduce FNs, but without much FP increase.
- Follows Principle 5: if we had stricter accuracy requirements, it would be simple enough to swap this out for a better model.

### CI Integration, Linters, etc
- Existing build automation: /Makefile, /scripts
- pytests to exercise parts of the Python Flask REST API, including dumping all JPEG files in the DB with a detected smile to a local directory. 
- Makefile has mypy linting baked in. That's it for now. ESLint, pylint, and shellcheck could be added down the line. Also black for autoformatting.
- CI Pipeline would be fairly straightforward to build from this. Generally you don't want too much of your build automation buried in yaml files...

### Packaging improvements
- Still using requirements.txt files with versions hardcoded... It would be better to move these to pyproject.toml and use slightly restrictive versions to avoid potential cross-platform dependency hell. 