Great — if the sockets won’t outlive the owning class and the count is dynamic, just store them by value in a std::vector<UdpSocket>. No new, no raw pointers.

Two small tweaks to make this safe:
	1.	Make UdpSocket non-copyable (to avoid double-closing the same fd).
	2.	Make it movable (so the vector can grow and relocate elements).

Here’s a tightened-up version plus a manager that owns “any number” of sockets:

#include <iostream>
#include <string>
#include <vector>
#include <stdexcept>
#include <cstring>
#include <arpa/inet.h>
#include <unistd.h>

class UdpSocket {
public:
    explicit UdpSocket(uint16_t localPort) : sockfd(-1), localPort_(localPort) {
        sockfd = socket(AF_INET, SOCK_DGRAM, 0);
        if (sockfd < 0) {
            perror("socket creation failed");
            throw std::runtime_error("Failed to create socket");
        }

        sockaddr_in localAddr{};
        localAddr.sin_family = AF_INET;
        localAddr.sin_addr.s_addr = INADDR_ANY;
        localAddr.sin_port = htons(localPort);

        if (bind(sockfd, (sockaddr*)&localAddr, sizeof(localAddr)) < 0) {
            perror("bind failed");
            close(sockfd);
            sockfd = -1;
            throw std::runtime_error("Failed to bind socket");
        }
    }

    ~UdpSocket() {
        if (sockfd >= 0) {
            close(sockfd);
        }
    }

    // Non-copyable (prevents double-close)
    UdpSocket(const UdpSocket&) = delete;
    UdpSocket& operator=(const UdpSocket&) = delete;

    // Movable (so std::vector can reallocate/move elements)
    UdpSocket(UdpSocket&& other) noexcept
        : sockfd(other.sockfd), localPort_(other.localPort_) {
        other.sockfd = -1;
        other.localPort_ = 0;
    }
    UdpSocket& operator=(UdpSocket&& other) noexcept {
        if (this != &other) {
            if (sockfd >= 0) close(sockfd);
            sockfd = other.sockfd;
            localPort_ = other.localPort_;
            other.sockfd = -1;
            other.localPort_ = 0;
        }
        return *this;
    }

    bool sendData(const std::string& ip, uint16_t port, const std::string& data) const {
        if (sockfd < 0) return false;

        sockaddr_in remoteAddr{};
        remoteAddr.sin_family = AF_INET;
        remoteAddr.sin_port = htons(port);

        if (inet_pton(AF_INET, ip.c_str(), &remoteAddr.sin_addr) <= 0) {
            perror("Invalid address");
            return false;
        }

        ssize_t sent = sendto(sockfd, data.data(), data.size(), 0,
                              (sockaddr*)&remoteAddr, sizeof(remoteAddr));
        if (sent < 0) {
            perror("sendto failed");
            return false;
        }
        return true;
    }

    uint16_t localPort() const { return localPort_; }

private:
    int sockfd;
    uint16_t localPort_{0};
};

class NetworkManager {
public:
    // Add a socket bound to a given port
    void addSocket(uint16_t port) {
        sockets.emplace_back(port);   // constructs in-place, no heap/new
    }

    // Send the same payload out of all sockets
    void broadcast(const std::string& ip, uint16_t port, const std::string& payload) {
        for (auto& s : sockets) {
            s.sendData(ip, port, payload);
        }
    }

    // Remove (and close) a socket by its local port
    bool removeByPort(uint16_t port) {
        auto it = std::remove_if(sockets.begin(), sockets.end(),
                                 [port](const UdpSocket& s){ return s.localPort() == port; });
        bool removed = (it != sockets.end());
        sockets.erase(it, sockets.end()); // destructors run for removed items
        return removed;
    }

    // Everything closes automatically when NetworkManager is destroyed
private:
    std::vector<UdpSocket> sockets;
};

int main() {
    try {
        NetworkManager nm;
        nm.addSocket(8080);
        nm.addSocket(9090);

        nm.broadcast("127.0.0.1", 8080, "Hello from all sockets");
        nm.removeByPort(9090); // optional example
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << "\n";
    }
}

Why this is nice:
	•	No new/delete anywhere.
	•	std::vector<UdpSocket> owns the sockets; when it resizes, it moves them safely.
	•	When NetworkManager dies, every UdpSocket’s destructor runs and closes its fd.

If you’ll be adding a lot, you can sockets.reserve(N) to reduce reallocations (moves are already cheap/safe here).