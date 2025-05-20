# Hydra-Once

A simple library for use on [hydra](https://github.com/facebookresearch/hydra) or [omegaconf](https://omegaconf.readthedocs.io/) configuration. The key feature is that this instantiate introduces the `_once_` key work, enabling objects marked with it to be instantiate as singletons 


## Motivation

Sometimes we want to ensure a subtree of the config is instantiated only ONCE. Making unnecessary copies, in these cases, can hammer resources or even break code.

Take this example:

```yaml
dataset:
  _target_: lightly.data.LightlyDataset
  root: data_dir
loader:
  _target_: torch.utils.data.DataLoader
  dataset: ${..dataset}  
  sampler:
    _target_: torch.utils.data.RandomSampler
    data_source: ${..dataset}.
```

Instantiating this config using hydra will, in fact, instantiate three separate instances of 'dataset', which is undesirable, because each one takes up memory. Even worse, calling instantiate a second time will create 3 more instances!

## Solution

We introduce a new keywork `_once_` to the config, which will ensure that the subtree is instantiated only once.

```yaml
dataset:
  _target_: lightly.data.LightlyDataset
  # setting _once_ to true, instantiate will only create this tree once, reusing it when needed.
  _once_: true                     
  # OPTIONAL: set _once_ to a string to manually use  instead of the default hash of the yaml
  # _once_: dataset_unique_key
  root: data_dir
loader:
  _target_: torch.utils.data.DataLoader
  dataset: ${..dataset}  
  sampler:
    _target_: torch.utils.data.RandomSampler
    data_source: ${..dataset}
```

Now, instantiate this config like so:

```python
from hydra_once import instantiate 

x = instantiate(cfg) # creates dataset just one time
y = instantiate(cfg) # creates dataset one more time
```

This will create the dataset and loader, but only instantiate the dataset once. By default, the cache used is ephemeral, and destroyed
at the end of the call to instantiate. 

To use a persistent cache, either set cache argument to a dictionary you reuse on subsequent calls, or to 'True' to use a global cache.

```python
from hydra_once import instantiate

cache = {} # or True

x = instantiate(cfg, cache=cache) # creates dataset one time
y = instantiate(cfg, cache=cache) # reuses dataset, but recreates loader 
```

To clear the global cache, use the clear function:

```python
from hydra_once import clear
clear() # clears the global cache
```
It is best to either use the default ephemeral cache, or a dictionary you control. Using the global cache can lead to hard to debug issues, especially in multi-threaded code.


## Fully Hydra Compatible

All hydra instantiate tests pass without modification using this library. Just replace the hydra instantiate function with the one in this library. 

```python
# from hydra.utils import instantiate
from hydra_once import instantiate
```

## Installation

```bash
pip install git+https://github.com/swamidass/hydra-once

```

This is python-only library, and only dependencies are hydra and omegaconf. 


