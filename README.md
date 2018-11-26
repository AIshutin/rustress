# rustress

rustress is a tiny module for predicting stress in russian words. Grabbed data from ruwiktionary, parser script, jupyter notebook with model creation are avaible on [github.com](https://github.com/AIshutin/rustress).

You can predict stress with using predict_stress in predictor.py

Example:

```
from rustress import predict_stress
print(predict_stress([input()]))
```