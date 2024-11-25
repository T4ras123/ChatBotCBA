from kubernetes import client, config
import json

def update_videos_configmap():
    # Load Kubernetes configuration from local kubeconfig
    config.load_kube_config()
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

if __name__ == "__main__":
    update_videos_configmap()