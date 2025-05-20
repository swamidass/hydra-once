# Hydra-Once

A simple library for use with [Hydra](https://github.com/facebookresearch/hydra) or [OmegaConf](https://omegaconf.readthedocs.io/) configurations. The key feature is the `_once_` keyword, which enables objects marked with it to be instantiated as singletons.

## Motivation

Sometimes, you want to ensure a subtree of your config is instantiated only **once**. Making unnecessary copies can waste resources or even break code.

**Example:**

```yaml
dataset:
  _target_: lightly.data.LightlyDataset
  root: data_dir
loader:
  _target_: torch.utils.data.DataLoader
  dataset: ${..dataset}  
  sampler:
    _target_: torch.utils.data.RandomSampler
    data_source: ${..dataset}
```

Instantiating this config with Hydra will create three separate instances of `dataset`, which is undesirable because each one takes up memory. Even worse, calling `instantiate` a second time will create three more instances!

## Solution

Hydra-Once introduces a new keyword, `_once_`, to the config. This ensures the subtree is instantiated only once.

```yaml
dataset:
  _target_: lightly.data.LightlyDataset
  _once_: true  # Only instantiate this tree once, reusing it as needed.
  # Optionally, set _once_ to a string to manually specify a cache key
  # _once_: dataset_unique_key
  root: data_dir
loader:
  _target_: torch.utils.data.DataLoader
  dataset: ${..dataset}  
  sampler:
    _target_: torch.utils.data.RandomSampler
    data_source: ${..dataset}
```

Now, instantiate your config like so:

```python
from hydra_once import instantiate

x = instantiate(cfg)  # creates dataset just one time
y = instantiate(cfg)  # creates dataset one more time
```

This will create the dataset and loader, but only instantiate the dataset once. By default, the cache is ephemeral and destroyed at the end of the call to `instantiate`.

## Persistent Caching

To use a persistent cache, set the `cache` argument to a dictionary you reuse, or to `True` to use a global cache:

```python
from hydra_once import instantiate

cache = {}  # or use True for a global cache

x = instantiate(cfg, cache=cache)  # creates dataset one time
y = instantiate(cfg, cache=cache)  # reuses dataset, but recreates loader
```

To clear the global cache, use the `clear` function:

```python
from hydra_once import clear
clear()  # clears the global cache
```

**Note:**  
It is best to use the default ephemeral cache or a dictionary you control. Using the global cache can lead to hard-to-debug issues, especially in multi-threaded code.

## Hydra Compatibility

All Hydra instantiate tests pass without modification using this library. Just replace the Hydra `instantiate` function with the one from this library:

```python
from hydra_once import instantiate
```

## Installation

```bash
pip install git+https://github.com/swamidass/hydra-once
```

This is a Python-only library. The only dependencies are Hydra and OmegaConf.

Let me know if you want any further customization or additional sections! PRs welcome.