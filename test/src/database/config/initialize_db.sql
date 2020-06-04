create schema chotuve;


create table chotuve.users
(
	email varchar,
	fullname varchar,
	phone_number varchar,
	photo varchar,
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

create table chotuve.api_keys
(
	alias varchar
		constraint api_keys_pk
			primary key,
	api_key varchar,
    health_endpoint varchar
);

create unique index api_keys_api_key_uindex
	on chotuve.api_keys (api_key);

create table chotuve.api_key_calls
(
	id serial
		constraint api_key_calls_pk
			primary key,
	alias varchar
		constraint api_key_calls_api_keys_alias_fk
			references chotuve.api_keys,
	path varchar,
    method varchar,
	status int,
    time float,
	timestamp timestamp
);