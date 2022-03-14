# BBM_Image_Organizer

Python script to analyze and sort Beaty Biodiversity Museum's pictures of animals.

# Setup Instructions

1. Based on you system architecture install Conda.

   Recommended: https://github.com/conda-forge/miniforge

2. Create an environment by

   ```
   conda env create -f beaty_env.yml
   ```

3. Activate the environment with
   ```
   conda activate beaty
   ```
   After a successful activation, something like `(beaty)` should show up in the terminal.

# PHP Instructions

View MAMP PHP Logs:

```
tail -f /Applications/MAMP/logs/php_error.log

```

# If Python import Issues, add the following to `~/.zprofile`

```
export PYTHONPATH=/Users/USERNAME/miniforge3/envs/beaty/lib/python3.9/site-packages:$PYTHONPATH
```
