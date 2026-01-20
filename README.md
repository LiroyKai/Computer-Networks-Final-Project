# Computer Networks Final Project 📡

**Course:** Computer Networks | **Institution:** HIT
**Topic:** TCP/IP Traffic Analysis & Python Chat Application (Socket Programming)

## 📋 Overview
This project consists of two main parts demonstrating theoretical and practical understanding of network layers:

1.  **Packet Encapsulation & Analysis:**
    * Generating synthetic HTTP traffic (CSV).
    * Simulating the encapsulation process (TCP/IP layers) using Jupyter Notebook.
    * Analyzing the generated traffic using Wireshark (`.pcap`).

2.  **Multi-Threaded Chat Application:**
    * A Python-based Chat Server supporting multiple clients simultaneously.
    * **GUI Client:** A graphical interface using `tkinter` for easy messaging.
    * **Protocol:** Custom implementation over TCP Sockets using Threading for non-blocking communication.

## 🚀 How to Run

### Prerequisites
* Python 3.x
* No external libraries required (uses standard `socket`, `threading`, `tkinter`).

### 1. Start the Server
Open a terminal and run:
```bash
python server.py
