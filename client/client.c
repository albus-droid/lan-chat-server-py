#include <stdio.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <netinet/in.h>
#include <string.h>
  
int main(int argc, char *argv[]) {

  struct sockaddr_in addr = {
    .sin_family = AF_INET,
    .sin_port   = htons(8080),
    .sin_addr.s_addr   = inet_addr("127.0.0.1")
  };

  int fd = socket(AF_INET, SOCK_STREAM, 0);

  connect(fd, (struct sockaddr *)&addr, sizeof(addr));

  char buf[1024], input[1024];

  int n; 

  while (1) {
    fd_set fds;
    FD_ZERO(&fds);
    FD_SET(fd, &fds);
    FD_SET(STDIN_FILENO, &fds);

    select(fd + 1, &fds, NULL, NULL, NULL);

    if (FD_ISSET(STDIN_FILENO, &fds)) {
      fgets(input, sizeof(input), stdin);
      write(fd, input, strlen(input));
    }

    if (FD_ISSET(fd, &fds)) {
      n = read(fd, buf, sizeof(buf) - 1);
      buf[n] = '\0';
      fputs(buf, stdout);
    }
  }

  close(fd);
  return 0;
}

