# experiment-manager
This repository provides an abstract class for managing, saving, and logging research-oriented experiments.

This abstract class acts as a lightweight experiment manager that automatically tracks, logs, and saves each experiment according to its title and hyperparameter specification. By checking whether logs and results already exist, it helps researchers skip re-running completed experiments, saving both time and computational resources while maintaining reproducibility.

# 🧪 experiment-manager

This repository provides an **abstract base class** for managing, saving, and logging **research-oriented experiments**.

It offers a unified interface you can subclass to standardize experiment execution, metadata handling, result persistence, and log management.

---

## 📁 Repository Structure

- **experiment.py** – contains the abstract base class `Experiment_abst`  
- **example.ipynb** – demonstrates how to subclass and use `Experiment_abst` in practice

---

## ⚙️ How It Works

When you inherit from `Experiment_abst`, your child class **must define** the following three static string attributes:

```python
experiment_description: str
experiment_title: str
experiment_unique_id: str
```

Your subclass must also **implement** a `run()` method that executes a single experiment run and populates the following member attributes:

```python
self.final_experiment_quality  # int
self.final_experiment_log      # str
self.final_experiment_data     # dict
```

---

### 🧭 Member Attributes That Should be Set by `run()`

#### `self.final_experiment_log`
A string describing the outcome or key observations of your experiment.  
It will be **automatically saved** in the `experiment_log` folder.

#### `self.final_experiment_data`
A dictionary containing the results, metrics, or artifacts of your experiment.  
It will be **automatically saved** (via pickle) in the `experiment_data` folder.

#### `self.final_experiment_quality`
An integer representing the **quality level** of your experiment.  
This value determines whether the results should be saved, depending on the threshold you set via the `save_result_quality_threshold` argument in `run_and_save_log()`.

For example:
```python
if accuracy < 0.8:  
    self.final_experiment_quality = 0
elif accuracy < 0.9: 
    self.final_experiment_quality = 1
else:                
    self.final_experiment_quality = 2
```

This mechanism ensures that **low-quality or failed runs are not saved**, while all runs’ logs remain recorded.

---

## 🚀 Running an Experiment

Use the `run_and_save_log()` method to execute your experiment:

```python
exp = MyExperiment(hyper_parameters)
results = exp.run_and_save_log(
    repeat_if_log_is_saved=False,
    save_log=True,
    save_result=True,
    save_result_quality_threshold=1
)
```

### Behavior:

- ✅ If a log for the same experiment already exists **and** `repeat_if_log_is_saved=False`,  
  the experiment **will not re-run**, and previously saved results will be returned.

- 🔁 If `repeat_if_log_is_saved=True`, or no log exists yet,  
  the experiment **will run again**.

This feature is especially useful during **research and paper writing**, where you may want to modify plots or analysis later without re-running expensive experiments.

---

## 🧩 Providing Hyperparameters

Hyperparameters should be passed as a dictionary when creating your experiment:

```python
params = {
    "lr": 0.001,
    "batch_size": 128,
    "_eval_param": 10
}
exp = MyExperiment(params)
```

In the above example, the experiment parameter specification string will be "lr_0d001_batch_size_128". This string is automatically logged and used to uniquely identify a specific hyperparameter configuration of an experiment. It also serves as a identifier for retrieving saved results and logs.

Note that the key '_eval_param' is not included in the specification string because its name starts with an underscore. If you don’t want a particular hyperparameter to be part of the experiment’s identifier, simply prefix its name with "_".

This is especially useful for parameters that don’t affect the model’s training process but might influence evaluation or post-processing. In this way, changing such a parameter won’t trigger a re-run of the experiment (when repeat_if_log_is_saved=False).

---

## 🛡️ Error Handling

If any exception occurs inside your `run()` function:
- The error is **automatically caught**
- A detailed **error log** (with traceback) is saved under `experiment_log/<experiment_title>/experiments_error_log.txt`
- Other experiments will **continue running**, preventing one failure from stopping the entire batch

---

## 📘 Example

See [`example.ipynb`](example.ipynb) for detailed usage and subclassing examples.

 
