import argparse
import collections
import re
import subprocess


NOTES_REF = 'refs/notes/votes'


Vote = collections.namedtuple('Vote', ['commit', 'user'])



def vote(args):
	assert args.user, 'TODO: determine user automatically'
	vote = 'vote:%s' % args.user
	subprocess.check_call([
		'git', 'notes', '--ref', NOTES_REF, 'append', '--allow-empty', '-m', vote, args.COMMIT],
		cwd=args.repo_dir)
	# TODO: prevent voting twice as same user


def get_all_votes(repo_dir):
	output_bytes = subprocess.check_output([
		'git', 'notes', '--ref', NOTES_REF, 'list'],
		cwd=repo_dir)
	output = output_bytes.decode('utf-8')
	for line in output.splitlines():
		if not line:
			continue
		votenote_ref, commit_id = line.split()
		# TODO use dulwich or something more efficient here
		votenote_bytes = subprocess.check_output(
			['git', 'show', votenote_ref],
			cwd=repo_dir)

		votenote_content = votenote_bytes.decode('utf-8') # TODO ignore invalid votes
		for voteline in votenote_content.splitlines():
			if not voteline:
				continue
			m = re.match(r'^vote:(?P<user>[a-z0-9@._]+)$', voteline.strip()) # TODO check re for user spec
			if not m:
				print('Skipping crap %r' % voteline)
				continue
			user = m.group('user')

			yield Vote(commit=commit_id, user=user)


def print_list(args):
	all_votes = get_all_votes(args.repo_dir)
	all_votes_sorted = sorted(all_votes, key=lambda v: (v.commit, v.user))
	for v in all_votes_sorted:
		print('%s: +1 from %s' % (v.commit, v.user))


def tally(all_votes):
	""" Returns a dict commit id => set of users """
	res = collections.defaultdict(set)
	for v in all_votes:
		res[v.commit].add(v.user)
	return res


def print_tally(args):
	all_votes = get_all_votes(args.repo_dir)
	for commit, votes in sorted(tally(all_votes).items(), key=lambda kv: (kv[1], kv[0])):
		print('%s: %d votes' % (commit, len(votes)))


def print_elect(args):
	all_votes = get_all_votes(args.repo_dir)
	winner_vcount, winner_commit = max((len(votes), commit) for commit, votes in tally(all_votes).items())
	# TODO more algorithms
	print('%s won the election with %d votes' % (winner_commit, winner_vcount))


def main():
	parser = argparse.ArgumentParser('Vote on git commands')
	parser.add_argument('-r', '--repo-dir', metavar='DIR', help='root directory of the repository to modify')
	subparsers = parser.add_subparsers(dest='cmd')
	vote_parser = subparsers.add_parser('vote', help='Vote for commit')
	vote_parser.add_argument('--user', metavar='USER_ID', help='ID of the user to vote as')
	vote_parser.add_argument('COMMIT', help='reference to the commit to vote for')
	subparsers.add_parser('list', help='List all votes')
	subparsers.add_parser('tally', help='Tally all votes')
	subparsers.add_parser('elect', help='Elect a commit')

	args = parser.parse_args()
	if args.cmd == 'vote':
		vote(args)
	elif args.cmd == 'list':
		print_list(args)
	elif args.cmd == 'tally':
		print_tally(args)
	elif args.cmd == 'elect':
		print_elect(args)
	else:
		parser.print_help()

if __name__ == '__main__':
	main()
