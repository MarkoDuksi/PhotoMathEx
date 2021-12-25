# PhotoMathEx

An example for a simple [Photomath](https://photomath.com/en/) "pretender" project as per assignment by the **Photomath** team. The assignment turned out to be inspiring enough to warrant further playing around.

## Description

Full assignment description is available here: https://github.com/photomath/ml-assignments/blob/main/assignment-A.pdf

## Motivation

Leeeeeearn! Help others.

## Usage

Command line execution example with output. Note: apparently, tensorflow routinely spits out lots of irrelevant info to _stderr._ No actual error messages were redirected to /dev/null.

```
>>> python photomathex.py
Provide valid image filenames as command line arguments.

>>> python photomathex.py non-existent.file test_images/0[1-4].jpg 2>/dev/null
Could not found: non-existent.file

from test_images/01.jpg:
0 + 1 + 2 + 3 - 4 - 5 * ( 6 + 7 - ( 8 + 9 ) ) = 22

from test_images/02.jpg:
3 * 8 - 4 * 2 / 4 * ( -( 3 + 9 ) ) = 48

from test_images/03.jpg:
4 + 6 - ( 10 - 3 ) * 2 / 8 * 3 = 4.75

from test_images/04.jpg:
1111111111111111111111 = 1111111111111111081984

from test_images/04.jpg:
2222222222222222222222 = 2222222222222222163968

from test_images/04.jpg:
3333333333333333333333 = 3333333333333333508096

from test_images/04.jpg:
4444444444444444444444 = 4444444444444444327936

from test_images/04.jpg:
5555555555555555555555 = 5555555555555555672064

from test_images/04.jpg:
6666666666666666666666 = 6666666666666667016192

from test_images/04.jpg:
7777777777777777777777 = 7777777777777777311744

from test_images/04.jpg:
8888888888888888888888 = 8888888888888888655872

from test_images/04.jpg:
9939999999999999993999 = 9939999999999998951424

from test_images/04.jpg:
0000000000000000000000 = 0

from test_images/04.jpg:
+ + + + + + + + + + + + + + + + + + + + + +
not a valid expression

from test_images/04.jpg:
- - - - - - - - - - - - - - - - - - - - - -
not a valid expression

from test_images/04.jpg:
* * * * * * * * * * * * * * * * * * * * * *
not a valid expression

from test_images/04.jpg:
/ / / / / / / / / / / / / / / / / / / / / /
not a valid expression

from test_images/04.jpg:
( ( ( ( ( ( ( ( ( ( ( ( ( ( ( ( ( ( ( ( ( (
not a valid expression

from test_images/04.jpg:
) ) ) ) ) ) ) ) ) ) ) ) ) ) ) ) ) ) ) ) ) )
not a valid expression
```

### Comments on the output results

For reference, these results should be compared to actual images in the [test_images](https://github.com/MarkoDuksi/PhotoMathEx/blob/main/test_images/) folder (more examples to follow). There are seemingly random trailing digits present after the first 16 digits of any non-zero number evaluated by the solver. This is due to limitations of internal representation of double-precision floating point numbers in python (and most probably any other representation adhering to [IEEE 754 specs](https://en.wikipedia.org/wiki/IEEE_754)). As can be seen in image [04.jpg](https://github.com/MarkoDuksi/PhotoMathEx/blob/main/test_images/04.jpg?raw=true), the 22-digit numbers were not meant to be solved. They were only meant to serve as a handy visual aid in evaluating classifier performance.

## Extractor module
Best not to repeat myself as the code is very well documented.

## Solver module
The solver was not implemented as a parse tree as normally thought in courses about data structures. Coming from Perl background I wanted to see if I can build a solver using just regular expressions and simple functions. Quick googling found no one who managed to do it and not for the lack of trying. Additionally, from previous experience in scraping GPX tracks with Beautiful Soup I learned that using even the quickest of all parsers, the lxml was multiple orders of magnitude slower than using regular expressions. Admittedly, speed is not an issue here but me accepting a challenge is. Regular expressions are ugly, there is no denying that fact ([need a reference?](https://github.com/back2root/log4shell-rex)). But sometimes they just do the job like nothing else can.

The whole implementation of the solver is more about validating the input than actually solving it. I wasn't required to do it, I just wanted some practice. The code is well documented which accounts for more than half of the content in the module, not including the test cases. The solver logic itself is contained in about 20 lines of code between two functions that call each other.

About 60 tests were run each in two different forms. Looking back, I should probably have written a random valid expression generator because there is still a chance that I have missed something in writing the tests manually. The solver result for each validated test expression was successfully compared with the result of python `eval`.

## Dataset
A dataset was built containing 120,016 images of decimal digits, operators "+", "-", "×", "/" and parentheses "(" and ")". Resources and the code that generates the dataset along with details of the process are available in the [01_Building_datasets](https://github.com/MarkoDuksi/PhotoMathEx/blob/main/notebooks/01_Building_datasets.ipynb) jupyter notebook. Dataset at a glance (ink fraction distribution across character classes):
![ink fraction distribution across character classes](https://github.com/MarkoDuksi/PhotoMathEx/blob/main/images/dataset.png)

## The model
Details in the [02_Building_a_classifier](https://github.com/MarkoDuksi/PhotoMathEx/blob/main/notebooks/02_Building_a_classifier.ipynb) jupyter notebook.

## Improvements proposal

### The dataset
- build a **high quality dataset:**
    - a high quality dataset is paramount to building a good model with dataset size taking the second place
    - choose **base fonts** more thoughtfully before applying augmentation
    - consider **separating various styles of writing some digits** (namely 4, 6, 7, and 9) into distinct classes
    - **pepper the dataset** with authentic paper imperfections generated by thresholding uniformly illuminated different blank sheets of paper

### The model
- build a **better CNN model:**
    - for this assignment the first guess to the CNN architecture yielded "reasonably" good results as per assignment requirements
    - experiment with modifying the model's architecture to all but eliminate a certain style of "9" being occasionally misclassified as a "3", if possible

### Extractor
- crop image to **discard marginal non-paper objects** (spiral bindings, parts of a desk, coffee mug...)
- improve **thresholding performance:**
    - **white balance** the BGR image before desaturating it
    - determine the optimal threshold value instead of making an educated guess
- **correct line distortions** in the image, enhancing line resolution power for multi-line and/or multiple expressions:
    - **cluster separate lines** into distinct clusters to avoid the Simpson's paradox
    - linear regression (fit to a quadratic curve) to **straighten and level the content of each line** by working only with residuals

### Solver
- **for higher accuracy,** if desired, implement **contextual error correcting** functionality to classifier predictions:
    - either by **programming it explicitly**
        - pros:
            - no large dataset required, only domain (math) knowledge
            - inherently explainable
            - computationally efficient
            - relatively easy and quick to implement
        - cons:
            - some typical misclassification examples are still needed for a general idea of the goal
    - or by training some sort of **RNN, GRU or LSTM** network model
        - pro:
            - in theory, it could generalize
        - con:
            - lacks any of the pros of the previous approach
- **expand solver's features**
    - add functionalities like:
        - **displaying every step it takes to arrive to the solution** (had it working for the purpose of debugging but refactored it out)
        - storing **intermediate subexpressions** in a database and checking if any have already been properly solved by Photomath math experts
        - **leveraging existent human-made stepwise solutions** to expressions or subexpressions
- **an AI solver** moonshot to aid and eventually replace some fraction of math experts
    - SWOT at a glance, besides the **O**bvious above:
        - a lot of manual solutions already exist as a **S**tarting point
        - every Photomath math expert presented with a suboptimal AI-generated "solution" will impr**O**ve it which becomes **feedback** to the model (to be thoroughly examined as to what kind off feedback to what type of model makes most, if any sense)
        - **W:** to reach the Moon it will probably take deep reinforcement learning which at this time might be computationally too expensive
        - as for **T,** I don't know, maybe Photomath gets sold to Google :-)
    - a journey of 384,400 km starts with a single step, so maybe tackle the simplest types of math problems first and build up from there
    - note: this is actually how I thought Photomath app worked until I caught a live Photomath Talk #4 and figured out there must have been a good reason this wasn't the case

## Left to be desired
I should mainly mention one point from the assignment that was left out from this implementation. Returning the coordinates of the detected characters extracted from the input image. Due to time constraints, this straightforward task of limited learning value gracefully surrendered to _"Don't stress too much about fulfilling all the requirements."_ instruction.

## Authors

Marko Dukši
[@LinkedIn](https://www.linkedin.com/in/mduksi/)

## Version History

- 0.1
    * Initial Release

## License

This project is licensed under the MIT License.
