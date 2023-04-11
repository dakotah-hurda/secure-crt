# securecrt-sessions
This package automatically generates SecureCRT Tree data based on our Source-of-Truth, Netbox. 

- The data in Netbox is loaded via the REST API and parsed. 

- The parsed data is then evaluated in order to make new "directories" for each Site or Site-Group. Nested site-groups are represented as "sub-directories" on the SecureCRT Tree.

- This repo is intended to be ran nightly via Git Actions and automatically sync'd with all admins' local repositories. This helps keep everyone's tree identical and makes sure everyone is on the same page. 

Current revision: 1.0.0 (WIP)

Authors:

- Ian May (ian.may@milwaukeecountywi.gov)
- Dakotah Hurda (dakotah.hurda@milwaukeecountywi.gov)