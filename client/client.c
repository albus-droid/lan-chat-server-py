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
  write(fd, argv[1], strlen(argv[1]));
  char buf[1024];

  int n; 
  while ((n = read(fd, buf, sizeof(buf) - 1)) > 0) {
    buf[n] = '\0';
    printf("%s", buf);
  }

  close(fd);
  return 0;
}

