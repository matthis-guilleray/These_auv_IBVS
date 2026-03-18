import rclpy

def create_client(node, message_type, topic, namespace_override=None):
    if namespace_override : 
        topic = "/" + namespace_override + topic
    else:
        topic = "/"+node.name_space + topic
    node.log("info", f"Creating client : {topic}")
    node.log("info", f"Message : {message_type}")
    cli = node.create_client(message_type, topic)
    result = False
    while not result:
        result = cli.wait_for_service(timeout_sec=4.0)
        node.log("info", "Client requested", once=True)
        node.log("warning", "Timeout on client request", skip_first=True)
    return cli

def call_service(node, client, message):
    node.log("info", client)
    future = client.call_async(message)
    rclpy.spin_until_future_complete(node, future, timeout_sec=3)

    if future.result() is not None:
        response = future.result()
        node.log("info", f"Response : {response}"
                
        )
    else:
        node.log("error",'Service call failed')