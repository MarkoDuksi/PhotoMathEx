# PhotoMathEx

A simple example project as per assignment by PhotoMath team.

## Description

Full assignment description is available here: https://github.com/photomath/ml-assignments/blob/main/assignment-A.pdf

## Usage example

Command line execution example with output:

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

### Comment on the results

For reference, these results should be compared to actual images in the [@test_images/](https://github.com/MarkoDuksi/PhotoMathEx/blob/main/test_images/) folder (more examples to follow). There are seemingly random trailing digits after the first 16 digits of any non-zero number evaluated by the solver. This is due to limitations of interal representation of double-precision floating point numbers in python (and most probably any other representation adhering to IEEE 754 specs). As can be seen in image [@04.jpg](https://github.com/MarkoDuksi/PhotoMathEx/blob/main/test_images/04.jpg?raw=true), 22-digit numbers are not ment to be evaluated. They are only ment to be visually compared for an ad-hoc evaluation of classifier accuracy.

## Additional Resources

A custom-made dataset of 120,016 images used to train the model is available in `dataset` folder. The dataset is in a pickled numpy array format and can be loaded by:
```
with open('dataset/math_dataset_md_1.0.pkl', 'rb') as file:
    test_dataset = pickle.load(file)
```
Dataset at a glance (ink fraction distribution across character classes)
![ink fraction distribution across character labels](https://github.com/MarkoDuksi/PhotoMathEx/blob/main/images/dataset.png)

### Comment on the dataset

Technical issues prevent uploading a large dataset. Will be investigated.

## TBD
- more info on building the dataset
- details on building and training the model
- follow-on discussion
- suggesting improvements

## Authors

Marko Dukši
[@LinkedIn](https://www.linkedin.com/in/mduksi/)

## Version History

- 0.1
    * Initial Release

## License

This project is licensed under the MIT License.
