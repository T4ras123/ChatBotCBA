from kubernetes import client, config

def update_videos_configmap():
    # Load in-cluster Kubernetes configuration
    config.load_incluster_config()
    v1 = client.CoreV1Api()

    # Read the updated videos.json content
    with open('videos.json', 'r') as f:
        videos_data = f.read()

    # Create the ConfigMap object
    config_map = client.V1ConfigMap(
        metadata=client.V1ObjectMeta(name='videos-config'),
        data={'videos.json': videos_data}
    )

    # Replace the existing ConfigMap
    v1.replace_namespaced_config_map(
        name='videos-config',
        namespace='default',  # Update if using a different namespace
        body=config_map
    )