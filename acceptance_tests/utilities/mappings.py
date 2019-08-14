from config import Config

QM_SUPPLIER = 'QM'
PPO_SUPPLIER = 'PPO'

QM3_2_DATASET = 'QM3.2'
QM3_4_DATASET = 'QM3.4'
PPD1_1_DATASET = 'PPD1.1'

PACK_CODE_TO_SFTP_DIRECTORY = {
    'P_IC_ICL1': Config.SFTP_PPO_DIRECTORY,
    'P_IC_ICL2B': Config.SFTP_PPO_DIRECTORY,
    'P_IC_ICL4': Config.SFTP_PPO_DIRECTORY,
    'P_IC_H1': Config.SFTP_QM_DIRECTORY,
    'P_IC_H2': Config.SFTP_QM_DIRECTORY,
    'P_IC_H4': Config.SFTP_QM_DIRECTORY,
    'P_OR_H1': Config.SFTP_QM_DIRECTORY,
    'P_OR_H2': Config.SFTP_QM_DIRECTORY,
    'P_OR_H2W': Config.SFTP_QM_DIRECTORY,
    'P_OR_H4': Config.SFTP_QM_DIRECTORY,
}

PACK_CODE_TO_DATASET = {
    'P_IC_ICL1': PPD1_1_DATASET,
    'P_IC_ICL2B': PPD1_1_DATASET,
    'P_IC_ICL4': PPD1_1_DATASET,
    'P_IC_H1': QM3_2_DATASET,
    'P_IC_H2': QM3_2_DATASET,
    'P_IC_H4': QM3_2_DATASET,
    'P_OR_H1': QM3_4_DATASET,
    'P_OR_H2': QM3_4_DATASET,
    'P_OR_H2W': QM3_4_DATASET,
    'P_OR_H4': QM3_4_DATASET,
}

PACK_CODE_TO_DESCRIPTION = {
    'P_IC_ICL1': 'Initial contact letter households - England',
    'P_IC_ICL2B': 'Initial contact letter households - Wales',
    'P_IC_ICL4': 'Initial contact letter households - Northern Ireland',
    'P_IC_H1': 'Initial contact questionnaire households - England',
    'P_IC_H2': 'Initial contact questionnaire households - Wales',
    'P_IC_H4': 'Initial contact questionnaire households - Northern Ireland',
    'P_OR_H1': 'Household Questionnaire for England',
    'P_OR_H2': 'Household Questionnaire for Wales (English)',
    'P_OR_H2W': 'Household Questionnaire for Wales (Welsh)',
    'P_OR_H4': 'Household Questionnaire for Northern Ireland (English)',

}
