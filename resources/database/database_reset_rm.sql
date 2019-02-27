DELETE FROM survey.classifiertype WHERE classifiertypeselectorfk IN ( SELECT classifiertypeselectorpk FROM survey.classifiertypeselector WHERE surveyfk in ( SELECT surveypk FROM survey.survey WHERE shortname LIKE 'Census%%'));
DELETE FROM survey.classifiertypeselector WHERE surveyfk in ( SELECT surveypk FROM survey.survey WHERE shortname LIKE 'Census%%');
DELETE FROM survey.survey WHERE shortname LIKE 'Census%%';

TRUNCATE collectionexercise.sampleunit CASCADE;
TRUNCATE collectionexercise.sampleunitgroup CASCADE;
TRUNCATE collectionexercise.samplelink CASCADE;
TRUNCATE collectionexercise.collectionexercise CASCADE;
TRUNCATE collectionexercise.casetypedefault CASCADE;
TRUNCATE collectionexercise.casetypeoverride CASCADE;

ALTER SEQUENCE collectionexercise.casetypedefaultseq RESTART WITH 1;
ALTER SEQUENCE collectionexercise.casetypeoverrideseq RESTART WITH 1;
ALTER SEQUENCE collectionexercise.sampleunitgrouppkseq RESTART WITH 1;
ALTER SEQUENCE collectionexercise.sampleunitpkseq RESTART WITH 1;
ALTER SEQUENCE collectionexercise.samplelinkpkseq RESTART WITH 1;

/* Clean Case DB */

TRUNCATE casesvc.case CASCADE;
TRUNCATE casesvc.caseevent CASCADE;
TRUNCATE casesvc.casegroup CASCADE;
TRUNCATE casesvc.response CASCADE;
TRUNCATE casesvc.caseiacaudit CASCADE;

ALTER SEQUENCE casesvc.caseeventseq RESTART WITH 1;
ALTER SEQUENCE casesvc.casegroupseq RESTART WITH 1;
ALTER SEQUENCE casesvc.caseseq RESTART WITH 1;
ALTER SEQUENCE casesvc.caserefseq RESTART WITH 1000000000000001;
ALTER SEQUENCE casesvc.responseseq RESTART WITH 1;
ALTER SEQUENCE casesvc.caseiacauditseq RESTART WITH 1;


/* Clean Action DB */

TRUNCATE action.action CASCADE;
TRUNCATE action.actionplanjob CASCADE;
TRUNCATE action.case CASCADE;
TRUNCATE action.messagelog CASCADE;
TRUNCATE action.actionplan CASCADE;
TRUNCATE action.actionrule CASCADE;

ALTER SEQUENCE action.actionpkseq RESTART WITH 1;
ALTER SEQUENCE action.actionplanjobseq RESTART WITH 1;
ALTER SEQUENCE action.casepkseq RESTART WITH 1;
ALTER SEQUENCE action.messageseq RESTART WITH 1;

/* Clean Action Exporter DB */

TRUNCATE actionexporter.actionrequest CASCADE;
TRUNCATE actionexporter.address CASCADE;
TRUNCATE actionexporter.contact CASCADE;
TRUNCATE actionexporter.filerowcount CASCADE;

ALTER SEQUENCE actionexporter.actionrequestpkseq RESTART WITH 1;
ALTER SEQUENCE actionexporter.contactpkseq RESTART WITH 1;

/* Reset Survey Sequences, these break the tests, not in existing acceptance tests; probably for that reason.
ALTER SEQUENCE survey.classifiertype_classifiertypepk_seq RESTART WITH 1;
ALTER SEQUENCE survey.classifiertype_classifiertypepk_seq1 RESTART WITH 1;
ALTER SEQUENCE survey.classifiertypeselector_classifiertypeselectorpk_seq RESTART WITH 1;
ALTER SEQUENCE survey.classifiertypeselector_classifiertypeselectorpk_seq1 RESTART WITH 1;
ALTER SEQUENCE survey.survey_surveypk_seq RESTART WITH 1;
ALTER SEQUENCE survey.survey_surveypk_seq1 RESTART WITH 1;
*/


/* Clean ras CI DB */
TRUNCATE ras_ci.survey CASCADE;
TRUNCATE ras_ci.exercise CASCADE;
TRUNCATE ras_ci.instrument_exercise CASCADE;
TRUNCATE ras_ci.seft_instrument CASCADE;
TRUNCATE ras_ci.instrument CASCADE;
TRUNCATE ras_ci.business CASCADE;
TRUNCATE ras_ci.instrument_business CASCADE;