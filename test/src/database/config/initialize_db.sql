create schema chotuve;


create table chotuve.users
(
	email varchar,
	fullname varchar,
	phone_number varchar,
	photo bytea,
	admin boolean,
	password varchar
);

create unique index users_email_uindex
	on chotuve.users (email);

alter table chotuve.users
	add constraint users_pk
		primary key (email);


create table chotuve.user_recovery_token
(
	email varchar,
	token varchar,
	timestamp timestamp,
	constraint email
		foreign key (email) references chotuve.users
);

create unique index user_recovery_token_email_uindex
	on chotuve.user_recovery_token (email);

alter table chotuve.user_recovery_token
	add constraint user_recovery_token_pk
		primary key (email);