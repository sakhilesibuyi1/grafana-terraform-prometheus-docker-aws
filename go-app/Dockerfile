# Start from the official golang image
FROM golang:1.17-alpine AS builder

# Set necessary environment variables needed for our image
ENV GO111MODULE=on \
    CGO_ENABLED=0 \
    GOOS=linux \
    GOARCH=amd64

# Move to working directory /build
WORKDIR /build

# Copy and download dependency using go mod
COPY go.mod .
COPY go.sum .
RUN go mod download

# Copy the code into the container
COPY . .

# Build the Go app
RUN go build -o app .

# Start from scratch (empty) image
FROM alpine:latest

# Copy the Pre-built binary file from the previous stage
COPY --from=builder /build/app /app

# Expose port 5001 to the outside world
EXPOSE 5001

# Command to run the executable
CMD ["/app"]
