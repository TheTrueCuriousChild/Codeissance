from concurrent import futures
import grpc

class NotificationServiceServicer:
    pass

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # Add gRPC service here
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()