package main

import (
	// "log"
	// "os"
	"context"
	// "net"
	"github.com/armon/go-socks5"
)

type CustomRewriter struct{}

func (r CustomRewriter) Rewrite(ctx context.Context, req *socks5.Request) (context.Context, *socks5.AddrSpec) {
	// Rewrite the destination to example.com:80
	newAddr := &socks5.AddrSpec{
		FQDN: "example.com",
		Port: 80,
	}
	return ctx, newAddr
}



func main() {
	// Create a SOCKS5 server
	
	conf := &socks5.Config{
		Rewriter: CustomRewriter{},
	}

	server, err := socks5.New(conf)
	if err != nil {
		panic(err)
	}

	// Create SOCKS5 proxy on localhost port 8000
	if err := server.ListenAndServe("tcp", "127.0.0.1:8000"); err != nil {
		panic(err)
	}
	// ad, err := net.ResolveIPAddr("ip", "github.com")
	// if (err == nil) {
	// 	println(string(ad.IP.String()))
	// } else {
	// 	println("hui")
	// }
	
}