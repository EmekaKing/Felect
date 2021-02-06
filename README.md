# Automatic Vision-Based Fault Detection on Electricity Transmission Components Using Very High-Resolution Imagery and Deep Learning Model

This repository is a step-by-step process that explores the use of high-resolution multispectral UAV-based oblique imagery for electric power transmission line component fault detection using the deep learning approach. 

This work developed in fulfilment of the requirements for the Erasmus Mundus degree of Master of Science in Geospatial Technologies. At the Universidade Nova de Lisboa Information Management School.
________
## Table of Contents

- [Automatic Vision-Based Fault Detection on Electricity Transmission Components Using Very High-Resolution Imagery and Deep Learning Model](#automatic-vision-based-fault-detection-on-electricity-transmission-components-using-very-high-resolution-imagery-and-deep-learning-model)
  - [Table of Contents](#table-of-contents)
  - [Description](#description)
  - [Technologies](#technologies)
  - [Actual Implementation](#actual-implementation)
  - [Acknowledgement](#acknowledgement)
  - [References & Appendix](#references--appendix)
  - [Authors Info](#authors-info)

________  
## Description
This study utilizes the Single Shot Multibox Detector (SSD), a one-stage object detection model on the electric transmission power line imagery to classify and detect faults present in the Shiroro - Kaduna Transmission network infrastructure, North West Nigeria. To achieve a solution to this problem, the first part of the implementation involved selection of suitable architecture and data pre-processing, which included the identification of faulty components (cracks, breakage, and corrosion) in the study area, image resizing (600 x 600), data labelling, and the generation of dataset features. The adopted network used a CNN based on a multiscale layer feature pyramid network (FPN) using aerial image patches and ground truth to localise and detect faults via a one-phase procedure. Several variations of the SSD architecture were employed to improve its efficiency to identify EPTN components’ faults.  Three parameters are used to determine the SSD-based models’ efficiency for the fault identification, namely mAP, overall accuracy, and the F1-score. The final developed SSD based models can seamlessly characterize and monitor both small- and large-scale faulty components from the imagery, thus achieving acceptable balance levels between global and local contexts. The proposed methodology and the results of this study provide a good basis for developing a system for electric power transmission network inspection to improve asset auditing and management and decision making by electric utilities. [For more info](docs/Introduction.md)

[Back to the top](#table-of-contents)
________

## Technologies
- Python
- jupyter notebook & Anaconda
- Tensorflow Object Detection API
- Node js (node package manager)
- Visual STudio Code
- notepad ++
- ArcGIS Pro
- Markdown
- Github

[Back to the top](#table-of-contents)
__________

## Actual Implementation
The [tutorial](docs/Installation.md) shows the process used to achieve this project.

[Back to the top](#table-of-contents)
__________

## Acknowledgement
I want to express our gratitude to my supervisor [Dr. Joel Dinis Baptista Ferreira da Silva](https://novaresearch.unl.pt/en/persons/joel-dinis-baptista-ferreira-da-silva) for his excellent guidance and support throughout this research. His valuable advice was the most significant help for me during this research. Also, I would like to appreciate his detailed and instructive comments on this research. To my co-supervisors, [Prof. Dr. Edzer Pebesma](https://www.uni-muenster.de/Geoinformatics/en/institute/staff/index.php/119/edzer_pebesma) and [Ditsuhi Iskandaryan](http://geotec.uji.es/staff/) (PhD in view), for their guidance, technical and constructive criticism on the thesis dissertation. 

[Back to the top](#table-of-contents)
___________

## References & Appendix
See [References](docs/References.md)

[Back to the top](#table-of-contents)
__________

## Authors Info
* *Chukwuemeka Fortune Igwe (M20190646@novaims.unl.pt)*