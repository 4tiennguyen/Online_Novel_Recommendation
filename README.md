# Novel_recomendation
A hybrid approach on Onlime Novel Recommendation System
# Requirements
anaconda python==3.10.4 torch==1.13.1 scipy==1.22.3 python-dateutil==2.8.2 pytz==2022.2.1 certifi==2022.12.07 numpy==1.22.3 dill==0.3.3 pyyaml==6.0 networkx==3.0 scikit-learn==1.2.1 numexpr==2.8.4 keras==2.3.1 six==1.15.0 theano==1.0.3 pandas==1.2.4 psutil==5.8.0 pympler==0.9 tensorflow==2.3.0 tables==3.6.1 scikit-optimize==0.8.1 python-telegram-bot==13.5
# Dataset
Datasets can be downloaded from: https://www.dropbox.com/sh/ur9amfhf9mag213/AAAtI7SWJft1WZZiR03nyDNCa?dl=0.  
Unzip the dataset file to the data folder, `./data/`

# Run Hybrid Model
STEP 1:
- Run NovelNet model to get recommendation lists and scores:   
&ensp;`python run_confg_NN.py conf/in_for_fiction_rec_more/84_NN.yml`
- The recommendation lists and scores are saved in .tien file
- For example: "C:\Users\tttie\OneDrive\Desktop\CS 274\NovelNet-main\rar_base_dir\84s-batch_size=1024-epochs=1-embedding_size=128-hidden_size=128-attribute_embedding_size=32-top=1-debug=False-model_version=v4-dot_product=True\result\\**0.tien**"  
Note: the epoch is now set to 1. You can increase it in 84_NN.yml. The results will be different. After running NovelNet model, by looking at the output you will know which epoch give the best score. Then we will have different .tien files such as 1.tien, 2.tien and 3.tien. Select the .tien file that have the best score for the hybrid model in STEP 3.  
  
STEP 2:
- Run STAN model to get recommendation lists and scores:  
&ensp;`python run_confg_stan.py conf/in_for_fiction_rec_more/84_Stan.yml`
- The recommendation lists and scores are saved in .csv file
- For example: 'C:\Users\tttie\OneDrive\Desktop\CS 274\NovelNet-main\rar_base_dir\stan-k=3000-sample_size=10000-lambda_spw=0.905-lambda_snh=100-lambda_inh=0.6/**stan_06.csv**'
  
STEP 3:
- Open 'hybrid_stant06_NN.ipynb'
- After loading libraries, change file paths to location (the two files in Step 1 and 2) they are saved
- Go to Experiment section, change the file path in save_weighted_score() function  
  
 OPTION: 
To run AR, open `run_confg_ar.py`, and go to line 569 to change the file path. Then run `python run_confg_ar.py conf/in_for_fiction_rec_more/84_AR.yml`  
To run the hybrid mode (NN+AR), do the same as STEP 3 with 'hybrid_AR_NN.ipynb'
