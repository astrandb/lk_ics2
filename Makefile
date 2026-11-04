bump:
	bumpver update --patch --no-fetch

bump_beta:
	bumpver update --no-fetch --patch --tag=beta --tag-num

bump_pre_next:
	bumpver update --no-fetch --tag-num

bump_final:
	bumpver update --no-fetch --tag=final

show_version:
	bumpver show --no-fetch
