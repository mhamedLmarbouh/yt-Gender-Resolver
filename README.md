# YouTube Comments Analytics: Gender Resolver

As a part of the YouTube Comments Analytics, this application is responsible of crawling the chanels of the users that posted each comment and then getting their Google+ account ID to fetch the associated gender information.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

To properly run the application, you will need to install the following programs and packages:
* [MongoDB Community Server 3.6.1](https://www.mongodb.com/download-center#community) - The database server 
* [Anaconda Distribution](https://www.anaconda.com/distribution/) - The python distribution for data science and analytics 
 you can get away with using just a basic conda install.

### Installing

After properly getting MongoDB and Anaconda (or Conda) you will need to prepare your workstation to deploy the project:

* Create the conda environment for the application, get to the root directory where the file environment.yml is located and run:

```
conda env create -f environment.yml
```


## Deployment

After completing the Installation steps, you are ready to run the application:

* Activate the conda conda environment:

```
activate untitled1
```
* Run the project by calling the main.py from the same console session where the environment is activated:

```
python main.py
```

## Authors

* **ESDAIRI Mohamed** 
* **LMARBOUH Mhamed** 


## Acknowledgments

* Greate thanks to the Dash Framework Community for the greate support.

