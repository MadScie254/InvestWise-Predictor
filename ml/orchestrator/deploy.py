"""
Prefect deployment configuration
"""
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule
from flows import training_flow, scheduled_retraining_flow, data_processing_flow

# Training pipeline deployment
training_deployment = Deployment.build_from_flow(
    flow=training_flow,
    name="ml-training-pipeline",
    version="1.0.0",
    work_queue_name="training",
    tags=["ml", "training", "production"],
    description="InvestWise ML model training pipeline",
    parameters={},
)

# Scheduled retraining deployment (weekly)
retraining_deployment = Deployment.build_from_flow(
    flow=scheduled_retraining_flow,
    name="scheduled-retraining",
    version="1.0.0",
    schedule=CronSchedule(cron="0 2 * * 0"),  # Every Sunday at 2 AM
    work_queue_name="training",
    tags=["ml", "training", "scheduled", "retraining"],
    description="Weekly scheduled model retraining",
    parameters={},
)

# Data processing deployment (daily)
data_processing_deployment = Deployment.build_from_flow(
    flow=data_processing_flow,
    name="data-processing-pipeline",
    version="1.0.0",
    schedule=CronSchedule(cron="0 1 * * *"),  # Every day at 1 AM
    work_queue_name="data",
    tags=["data", "processing", "scheduled"],
    description="Daily data processing and preparation",
    parameters={},
)

if __name__ == "__main__":
    # Deploy all flows
    training_deployment.apply()
    retraining_deployment.apply()
    data_processing_deployment.apply()
    
    print("All deployments created successfully!")
    print("Training deployment: ml-training-pipeline")
    print("Retraining deployment: scheduled-retraining (weekly)")
    print("Data processing deployment: data-processing-pipeline (daily)")