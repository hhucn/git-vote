import argparse

def vote(args):
	pass


def main():
	parser = argparse.ArgumentParser('Vote on git commands')
	subparsers = parser.add_subparsers(dest='cmd')
	vote_parser = subparsers.add_parser('vote')

	args = parser.parse_args()
	if args.cmd == 'vote':
		vote(args)
	else:
		assert False

if __name__ == '__main__':
	main()
