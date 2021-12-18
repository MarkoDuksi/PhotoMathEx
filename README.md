# PhotoMathEx

An example for a simple [Photomath](https://photomath.com/en/) "pretender" project as per assignment by the **Photomath** team.

## Description

Full assignment description is available here: https://github.com/photomath/ml-assignments/blob/main/assignment-A.pdf

## Motivation

Leeeeeearn! Help others.

## Usage example

Command line execution example with output. Note: apparently, tensorflow routinely spits out lots of irrelevant info to _stderr._ No actual error messages were redirected to /dev/null.

```
>>> python photomathex.py test_images/0[1-4].jpg 2>/dev/null

from test_images/01.jpg: 0 + 1 + 2 + 3 - 4 - 5 * ( 6 + 7 - ( 8 + 9 ) )
result = 22

from test_images/02.jpg: 3 * 8 - 4 * 2 / 4 * ( - ( 3 + 9 ) )
result = 48

from test_images/03.jpg: 4 + 6 - ( 1 0 - 3 ) * 2 / 8 * 3
result = 4.75

from test_images/04.jpg: 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
result = 1111111111111111081984

from test_images/04.jpg: 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2
result = 2222222222222222163968

from test_images/04.jpg: 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3
result = 3333333333333333508096

from test_images/04.jpg: 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4
result = 4444444444444444327936

from test_images/04.jpg: 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5
result = 5555555555555555672064

from test_images/04.jpg: 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6
result = 6666666666666667016192

from test_images/04.jpg: 7 7 7 7 7 7 7 7 7 7 7 7 7 7 7 7 7 7 7 7 7 7
result = 7777777777777777311744

from test_images/04.jpg: 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8
result = 8888888888888888655872

from test_images/04.jpg: 9 9 3 9 9 9 9 9 9 9 9 9 9 9 9 9 9 9 3 9 9 9
result = 9939999999999998951424

from test_images/04.jpg: 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
result = 0

from test_images/04.jpg: + + + + + + + + + + + + + + + + + + + + + +
not a valid expression

from test_images/04.jpg: - - - - - - - - - - - - - - - - - - - - - -
not a valid expression

from test_images/04.jpg: * * * * * * * * * * * * * * * * * * * * * *
not a valid expression

from test_images/04.jpg: / / / / / / / / / / / / / / / / / / / / / /
not a valid expression

from test_images/04.jpg: ( ( ( ( ( ( ( ( ( ( ( ( ( ( ( ( ( ( ( ( ( (
not a valid expression

from test_images/04.jpg: ) ) ) ) ) ) ) ) ) ) ) ) ) ) ) ) ) ) ) ) ) )
not a valid expression
```

### Comments on the output results

For reference, these results should be compared to actual images in the [test_images](https://github.com/MarkoDuksi/PhotoMathEx/blob/main/test_images/) folder (more examples to follow). There are seemingly random trailing digits present after the first 16 digits of any non-zero number evaluated by the solver. This is due to limitations of internal representation of double-precision floating point numbers in python (and most probably any other representation adhering to [IEEE 754 specs](https://en.wikipedia.org/wiki/IEEE_754)). As can be seen in image [04.jpg](https://github.com/MarkoDuksi/PhotoMathEx/blob/main/test_images/04.jpg?raw=true), the 22-digit numbers were not meant to be evaluated. They were only meant to be visually compared for an ad-hoc evaluation of classifier performance.

## Additional Resources

A custom-made dataset of 120,016 images used to train the model is available in [dataset](https://github.com/MarkoDuksi/PhotoMathEx/blob/main/dataset/) folder. The dataset is in a pickled numpy array format (compressed using *gzip,* 95 MB after uncompressing) and can be loaded by:
```
with open('dataset/math_dataset_md_1.0.pkl', 'rb') as file:
    dataset = pickle.load(file)
```
Dataset at a glance (ink fraction distribution across character classes):
![ink fraction distribution across character classes](https://github.com/MarkoDuksi/PhotoMathEx/blob/main/images/dataset.png)

Class labels were named with [POSIX compliance](https://www.ibm.com/docs/en/zos/2.3.0?topic=locales-posix-portable-file-name-character-set) in mind since the images of generated dataset samples were also stored in a labeled directory structure. This facilitated visual inspection of generated samples which was especially important for evaluating outlier detection.

## Additional Resources

A custom-made dataset of 120,016 images used to train the model is available in [dataset](https://github.com/MarkoDuksi/PhotoMathEx/blob/main/dataset/) folder. The dataset is in a pickled numpy array format (compressed using gzip, 95 MB after uncompressing) and can be loaded by:
```
with open('dataset/math_dataset_md_1.0.pkl', 'rb') as file:
    dataset = pickle.load(file)
```
Dataset at a glance (ink fraction distribution across character classes):
![ink fraction distribution across character labels](https://github.com/MarkoDuksi/PhotoMathEx/blob/main/images/dataset.png)

## Improvements proposal

### Extractor
- crop image to **discard marginal non-paper objects** (spiral bindings, parts of a desk, coffee mug...)
- improve **thresholding reliability:**
    - **white balance** the BGR image before desaturating it
    - add a smoothed inverse light frame to level up the uneven lighting (including large shadows) - let's call it "poor man's HDR"
- **undistort lines of content** in the image, enhancing line resolution power for multi-line and/or multiple expressions:
    - **cluster separate lines** into distinct clusters to avoid the Simpson's paradox
    - consider **multi-label QDA on "line" clusters** to bump up the line resolution power (evaluate computational cost vs. expected benefit)
    - linear regression (fit to a quadratic curve) to **straighten and level the content of a line** (working on residuals) to raise character resolution power

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
        -pro:
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

## TBD
- a few docstrings in the solver module
- refactor the code
- more info on building the dataset (image-editing skills built through decades of photography experience came in really handy here)
- details on building and training the model (nothing spectacular)
- discussion of model performance (nothing spectacular)
- more visuals in this README
- maybe process some fun example images-expressions

## Left to be desired
By my criteria - a lot. But I should mainly mention one point from the assignment that was left out from this implementation. Returning the coordinates of the detected characters extracted from the input image. Due to time constraints, this straightforward task of limited learning value surrendered to _"Don't stress too much about fulfilling all the requirements."_ instruction.

## Authors

Marko Dukši
[@LinkedIn](https://www.linkedin.com/in/mduksi/)

## Version History

- 0.1
    * Initial Release

## License

This project is licensed under the MIT License.
