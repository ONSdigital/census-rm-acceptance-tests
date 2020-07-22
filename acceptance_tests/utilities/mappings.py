from config import Config

QM3_2_DATASET = 'QM3.2'
QM3_3_DATASET = 'QM3.3'
QM3_4_DATASET = 'QM3.4'
PPD1_1_DATASET = 'PPD1.1'
PPD1_2_DATASET = 'PPD1.2'
PPD1_3_DATASET = 'PPD1.3'
PPD1_6_DATASET = 'PPD1.6'
PPD1_7_DATASET = 'PPD1.7'
PPD1_8_DATASET = 'PPD1.8'

DEFAULT_CLASSIFIERS = "case_type != 'HI' AND "

CLASSIFIERS_FOR_ACTION_TYPE = {
    'FIELD': "treatment_code IN ('HH_QF2R1E')",

    'ICL1E': "treatment_code IN ('HH_LFNR1E', 'HH_LFNR2E', 'HH_LFNR3AE', 'HH_LF2R1E', 'HH_LF2R2E', "
             "'HH_LF2R3AE', 'HH_LF2R3BE', 'HH_LF3R1E', 'HH_LF3R2E', 'HH_LF3R3AE', 'HH_LF3R3BE')",
    'ICL2W': "treatment_code IN ('HH_LFNR1W', 'HH_LFNR2W', 'HH_LFNR3AW', 'HH_LF2R1W', 'HH_LF2R2W', "
             "'HH_LF2R3AW', 'HH_LF2R3BW', 'HH_LF3R1W', 'HH_LF3R2W', 'HH_LF3R3AW', 'HH_LF3R3BW')",
    'ICL4N': "treatment_code IN ('HH_1LSFN', 'HH_2LEFN')",
    'ICHHQE': "treatment_code IN ('HH_QF2R1E', 'HH_QF2R2E', 'HH_QF2R3AE', 'HH_QF3R1E', 'HH_QF3R2E', "
              "'HH_QF3R3AE')",
    'ICHHQW': "treatment_code IN ('HH_QF2R1W', 'HH_QF2R2W', 'HH_QF2R3AW', 'HH_QF3R1W', 'HH_QF3R2W', "
              "'HH_QF3R3AW')",
    'ICHHQN': "treatment_code IN ('HH_3QSFN')",

    'P_RL_1RL1_1': "treatment_code IN ('HH_LF2R1E', 'HH_LF3R1E', 'HH_LFNR1E', 'HH_QF2R1E', 'HH_QF3R1E', "
                   "'HH_QFNR1E') AND survey_launched = 'f'",
    'P_RL_2RL2B_3a': "treatment_code IN ('HH_LF2R3AW', 'HH_LF3R3AW', 'HH_LFNR3AW', 'HH_QF2R3AW', 'HH_QF3R3AW',"
                     " 'HH_QFNR3AW')",
    'P_QU_H2': "treatment_code IN ('HH_LF2R3BW', 'HH_LF3R3BW', 'HH_LFNR3BW')",
    'CE1_IC01': "treatment_code IN ('CE_LDCEE')",
    'CE1_IC02': "treatment_code IN ('CE_LDCEW')",
    'CE_IC03': "treatment_code IN ('CE_LDIEE')",
    'CE_IC04': "treatment_code IN ('CE_LDIEW')",
    'CE_IC03_1': "treatment_code IN ('CE_LDIUE')",
    'CE_IC04_1': "treatment_code IN ('CE_LDIUW')",
    'CE_IC05': "treatment_code IN ('CE_2LNFN')",
    'CE_IC06': "treatment_code IN ('CE_3LSNFN')",
    'CE_IC08': "treatment_code IN ('CE_1QNFN')",
    'CE_IC09': "treatment_code IN ('CE_QDIEE')",
    'CE_IC10': "treatment_code IN ('CE_QDIEW')",
    'SPG_IC11': "treatment_code IN ('SPG_LPHUE')",
    'SPG_IC12': "treatment_code IN ('SPG_LPHUW')",
    'SPG_IC13': "treatment_code IN ('SPG_QDHUE')",
    'SPG_IC14': "treatment_code IN ('SPG_QDHUW')",
    'P_RD_2RL1_1': "lsoa IN ('E01014540', 'E01014541', 'E01014542', 'W01014540')",
    'P_RD_2RL2B_1': "lsoa IN ('E01014669', 'W01014669')",
    'P_RD_2RL1_2': "lsoa IN ('E01014543', 'E01014544')",
    'P_RD_2RL2B_2': "lsoa IN ('E01033361', 'E01015005', 'W01033361', 'W01015005')",
    'P_RD_2RL1_3': "lsoa IN ('E01014545')",
    'P_RD_2RL2B_3': "lsoa IN ('E01014897', 'W01014897')",
    'P_RL_1RL1A': "lsoa IN ('E01014540', 'E01014541', 'E01014542') AND survey_launched = 't'",
    'P_RL_1RL2BA': "lsoa IN ('E01014669', 'W01014669') AND survey_launched = 't'",
    'P_RL_2RL1A': "lsoa IN ('E01014543', 'E01014544') AND survey_launched = 't'",
    'P_RL_2RL2BA': "lsoa IN ('E01033361', 'E01015005', 'W01033361', 'W01015005') AND survey_launched = 't'",
}

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
    'P_OR_HC1': Config.SFTP_QM_DIRECTORY,
    'P_OR_HC2': Config.SFTP_QM_DIRECTORY,
    'P_OR_HC2W': Config.SFTP_QM_DIRECTORY,
    'P_OR_HC4': Config.SFTP_QM_DIRECTORY,
    "P_LP_HL1": Config.SFTP_PPO_DIRECTORY,
    "P_LP_HL2": Config.SFTP_PPO_DIRECTORY,
    "P_LP_HL2W": Config.SFTP_PPO_DIRECTORY,
    "P_LP_HL4": Config.SFTP_PPO_DIRECTORY,
    "P_LP_ILP1": Config.SFTP_PPO_DIRECTORY,
    "P_LP_ILP2": Config.SFTP_PPO_DIRECTORY,
    "P_LP_ILP2W": Config.SFTP_PPO_DIRECTORY,
    "P_LP_IL4": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBALB1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBAMH1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBARA1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBARA2": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBARA4": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBARM1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBBEN1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBBEN2": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBBOS1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBBUL1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBBUL2": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBBUL4": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBBUR1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBCAN1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBCAN2": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBCAN4": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBCZE1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBCZE4": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBFAR1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBFAR2": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBFRE1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBGER1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBGRE1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBGRE2": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBGUJ1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBPAN1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBPAN2": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBHEB1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBHIN1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBHUN1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBHUN4": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBIRI4": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBITA1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBITA2": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBJAP1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBKOR1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBKUR1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBKUR2": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBLAT1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBLAT2": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBLAT4": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBLIN1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBLIT1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBLIT4": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBMAL1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBMAL2": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBMAN1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBMAN2": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBMAN4": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBNEP1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBPAS1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBPAS2": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBPOL1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBPOL2": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBPOL4": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBPOR1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBPOR2": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBPOR4": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBPOT1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBROM1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBROM4": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBRUS1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBRUS2": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBRUS4": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBSLE1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBSLO1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBSLO4": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBSOM1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBSOM4": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBSPA1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBSPA2": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBSWA1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBSWA2": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBTAG1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBTAM1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBTHA1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBTHA2": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBTET4": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBTIG1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBTUR1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBUKR1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBULS4": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBURD1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBVIE1": Config.SFTP_PPO_DIRECTORY,
    "P_TB_TBYSH1": Config.SFTP_PPO_DIRECTORY,
    "P_OR_I1": Config.SFTP_QM_DIRECTORY,
    "P_OR_I2": Config.SFTP_QM_DIRECTORY,
    "P_OR_I2W": Config.SFTP_QM_DIRECTORY,
    "P_OR_I4": Config.SFTP_QM_DIRECTORY,
    "P_RL_1RL1_1": Config.SFTP_PPO_DIRECTORY,
    "P_RL_2RL2B_3a": Config.SFTP_PPO_DIRECTORY,
    "P_QU_H1": Config.SFTP_QM_DIRECTORY,
    "P_QU_H2": Config.SFTP_QM_DIRECTORY,
    "P_QU_H4": Config.SFTP_QM_DIRECTORY,
    "P_RD_2RL1_1": Config.SFTP_PPO_DIRECTORY,
    "P_RD_2RL2B_1": Config.SFTP_PPO_DIRECTORY,
    "P_RD_2RL1_2": Config.SFTP_PPO_DIRECTORY,
    "P_RD_2RL2B_2": Config.SFTP_PPO_DIRECTORY,
    "P_RD_2RL1_3": Config.SFTP_PPO_DIRECTORY,
    "P_RD_2RL2B_3": Config.SFTP_PPO_DIRECTORY,
    "P_RL_1RL1A": Config.SFTP_PPO_DIRECTORY,
    "P_RL_1RL2BA": Config.SFTP_PPO_DIRECTORY,
    "P_RL_2RL1A": Config.SFTP_PPO_DIRECTORY,
    "P_RL_2RL2BA": Config.SFTP_PPO_DIRECTORY,
    "P_RL_1IRL1": Config.SFTP_PPO_DIRECTORY,
    "P_RL_1IRL2B": Config.SFTP_PPO_DIRECTORY,
    "D_CE1A_ICLCR1": Config.SFTP_PPO_DIRECTORY,
    "D_CE1A_ICLCR2B": Config.SFTP_PPO_DIRECTORY,
    "D_ICA_ICLR1": Config.SFTP_PPO_DIRECTORY,
    "D_ICA_ICLR2B": Config.SFTP_PPO_DIRECTORY,
    "D_CE4A_ICLR4": Config.SFTP_PPO_DIRECTORY,
    "D_CE4A_ICLS4": Config.SFTP_PPO_DIRECTORY,
    "D_FDCE_I4": Config.SFTP_QM_DIRECTORY,
    "D_FDCE_I1": Config.SFTP_QM_DIRECTORY,
    "D_FDCE_I2": Config.SFTP_QM_DIRECTORY,
    "D_FDCE_H1": Config.SFTP_QM_DIRECTORY,
    "D_FDCE_H2": Config.SFTP_QM_DIRECTORY,
    "P_ICCE_ICL1": Config.SFTP_PPO_DIRECTORY,
    "P_ICCE_ICL2B": Config.SFTP_PPO_DIRECTORY,
    "P_UAC_UACIP1": Config.SFTP_PPO_DIRECTORY,
    "P_UAC_UACIP2B": Config.SFTP_PPO_DIRECTORY,
    "P_UAC_UACIP4": Config.SFTP_PPO_DIRECTORY,
    "P_UAC_UACHHP1": Config.SFTP_PPO_DIRECTORY,
    "P_UAC_UACHHP2B": Config.SFTP_PPO_DIRECTORY,
    "P_UAC_UACHHP4": Config.SFTP_PPO_DIRECTORY,
    "P_ER_ILER1": Config.SFTP_PPO_DIRECTORY,
    "P_ER_ILER2B": Config.SFTP_PPO_DIRECTORY,
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
    'P_OR_HC1': QM3_4_DATASET,
    'P_OR_HC2': QM3_4_DATASET,
    'P_OR_HC2W': QM3_4_DATASET,
    'P_OR_HC4': QM3_4_DATASET,
    "P_LP_HL1": PPD1_3_DATASET,
    "P_LP_HL2": PPD1_3_DATASET,
    "P_LP_HL2W": PPD1_3_DATASET,
    "P_LP_HL4": PPD1_3_DATASET,
    "P_LP_ILP1": PPD1_3_DATASET,
    "P_LP_ILP2": PPD1_3_DATASET,
    "P_LP_ILP2W": PPD1_3_DATASET,
    "P_LP_IL4": PPD1_3_DATASET,
    "P_TB_TBALB1": PPD1_3_DATASET,
    "P_TB_TBAMH1": PPD1_3_DATASET,
    "P_TB_TBARA1": PPD1_3_DATASET,
    "P_TB_TBARA2": PPD1_3_DATASET,
    "P_TB_TBARA4": PPD1_3_DATASET,
    "P_TB_TBARM1": PPD1_3_DATASET,
    "P_TB_TBBEN1": PPD1_3_DATASET,
    "P_TB_TBBEN2": PPD1_3_DATASET,
    "P_TB_TBBOS1": PPD1_3_DATASET,
    "P_TB_TBBUL1": PPD1_3_DATASET,
    "P_TB_TBBUL2": PPD1_3_DATASET,
    "P_TB_TBBUL4": PPD1_3_DATASET,
    "P_TB_TBBUR1": PPD1_3_DATASET,
    "P_TB_TBCAN1": PPD1_3_DATASET,
    "P_TB_TBCAN2": PPD1_3_DATASET,
    "P_TB_TBCAN4": PPD1_3_DATASET,
    "P_TB_TBCZE1": PPD1_3_DATASET,
    "P_TB_TBCZE4": PPD1_3_DATASET,
    "P_TB_TBFAR1": PPD1_3_DATASET,
    "P_TB_TBFAR2": PPD1_3_DATASET,
    "P_TB_TBFRE1": PPD1_3_DATASET,
    "P_TB_TBGER1": PPD1_3_DATASET,
    "P_TB_TBGRE1": PPD1_3_DATASET,
    "P_TB_TBGRE2": PPD1_3_DATASET,
    "P_TB_TBGUJ1": PPD1_3_DATASET,
    "P_TB_TBPAN1": PPD1_3_DATASET,
    "P_TB_TBPAN2": PPD1_3_DATASET,
    "P_TB_TBHEB1": PPD1_3_DATASET,
    "P_TB_TBHIN1": PPD1_3_DATASET,
    "P_TB_TBHUN1": PPD1_3_DATASET,
    "P_TB_TBHUN4": PPD1_3_DATASET,
    "P_TB_TBIRI4": PPD1_3_DATASET,
    "P_TB_TBITA1": PPD1_3_DATASET,
    "P_TB_TBITA2": PPD1_3_DATASET,
    "P_TB_TBJAP1": PPD1_3_DATASET,
    "P_TB_TBKOR1": PPD1_3_DATASET,
    "P_TB_TBKUR1": PPD1_3_DATASET,
    "P_TB_TBKUR2": PPD1_3_DATASET,
    "P_TB_TBLAT1": PPD1_3_DATASET,
    "P_TB_TBLAT2": PPD1_3_DATASET,
    "P_TB_TBLAT4": PPD1_3_DATASET,
    "P_TB_TBLIN1": PPD1_3_DATASET,
    "P_TB_TBLIT1": PPD1_3_DATASET,
    "P_TB_TBLIT4": PPD1_3_DATASET,
    "P_TB_TBMAL1": PPD1_3_DATASET,
    "P_TB_TBMAL2": PPD1_3_DATASET,
    "P_TB_TBMAN1": PPD1_3_DATASET,
    "P_TB_TBMAN2": PPD1_3_DATASET,
    "P_TB_TBMAN4": PPD1_3_DATASET,
    "P_TB_TBNEP1": PPD1_3_DATASET,
    "P_TB_TBPAS1": PPD1_3_DATASET,
    "P_TB_TBPAS2": PPD1_3_DATASET,
    "P_TB_TBPOL1": PPD1_3_DATASET,
    "P_TB_TBPOL2": PPD1_3_DATASET,
    "P_TB_TBPOL4": PPD1_3_DATASET,
    "P_TB_TBPOR1": PPD1_3_DATASET,
    "P_TB_TBPOR2": PPD1_3_DATASET,
    "P_TB_TBPOR4": PPD1_3_DATASET,
    "P_TB_TBPOT1": PPD1_3_DATASET,
    "P_TB_TBROM1": PPD1_3_DATASET,
    "P_TB_TBROM4": PPD1_3_DATASET,
    "P_TB_TBRUS1": PPD1_3_DATASET,
    "P_TB_TBRUS2": PPD1_3_DATASET,
    "P_TB_TBRUS4": PPD1_3_DATASET,
    "P_TB_TBSLE1": PPD1_3_DATASET,
    "P_TB_TBSLO1": PPD1_3_DATASET,
    "P_TB_TBSLO4": PPD1_3_DATASET,
    "P_TB_TBSOM1": PPD1_3_DATASET,
    "P_TB_TBSOM4": PPD1_3_DATASET,
    "P_TB_TBSPA1": PPD1_3_DATASET,
    "P_TB_TBSPA2": PPD1_3_DATASET,
    "P_TB_TBSWA1": PPD1_3_DATASET,
    "P_TB_TBSWA2": PPD1_3_DATASET,
    "P_TB_TBTAG1": PPD1_3_DATASET,
    "P_TB_TBTAM1": PPD1_3_DATASET,
    "P_TB_TBTHA1": PPD1_3_DATASET,
    "P_TB_TBTHA2": PPD1_3_DATASET,
    "P_TB_TBTET4": PPD1_3_DATASET,
    "P_TB_TBTIG1": PPD1_3_DATASET,
    "P_TB_TBTUR1": PPD1_3_DATASET,
    "P_TB_TBUKR1": PPD1_3_DATASET,
    "P_TB_TBULS4": PPD1_3_DATASET,
    "P_TB_TBURD1": PPD1_3_DATASET,
    "P_TB_TBVIE1": PPD1_3_DATASET,
    "P_TB_TBYSH1": PPD1_3_DATASET,
    "P_UAC_UACHHP1": PPD1_3_DATASET,
    "P_UAC_UACHHP2B": PPD1_3_DATASET,
    "P_UAC_UACHHP4": PPD1_3_DATASET,
    "P_ER_ILER1": PPD1_3_DATASET,
    "P_ER_ILER2B": PPD1_3_DATASET,
    "P_OR_I1": QM3_4_DATASET,
    "P_OR_I2": QM3_4_DATASET,
    "P_OR_I2W": QM3_4_DATASET,
    "P_OR_I4": QM3_4_DATASET,
    "P_RL_1RL1_1": PPD1_2_DATASET,
    "P_RL_2RL2B_3a": PPD1_2_DATASET,
    "P_QU_H1": QM3_3_DATASET,
    "P_QU_H2": QM3_3_DATASET,
    "P_QU_H4": QM3_3_DATASET,
    "P_RD_2RL1_1": PPD1_2_DATASET,
    "P_RD_2RL2B_1": PPD1_2_DATASET,
    "P_RD_2RL1_2": PPD1_2_DATASET,
    "P_RD_2RL2B_2": PPD1_2_DATASET,
    "P_RD_2RL1_3": PPD1_2_DATASET,
    "P_RD_2RL2B_3": PPD1_2_DATASET,
    "P_RL_1RL1A": PPD1_2_DATASET,
    "P_RL_1RL2BA": PPD1_2_DATASET,
    "P_RL_2RL1A": PPD1_2_DATASET,
    "P_RL_2RL2BA": PPD1_2_DATASET,
    "P_RL_1IRL1": PPD1_2_DATASET,
    "P_RL_1IRL2B": PPD1_2_DATASET,
    "D_CE1A_ICLCR1": PPD1_7_DATASET,
    "D_CE1A_ICLCR2B": PPD1_7_DATASET,
    "D_ICA_ICLR1": PPD1_7_DATASET,
    "D_ICA_ICLR2B": PPD1_7_DATASET,
    "P_ICCE_ICL1": PPD1_7_DATASET,
    "P_ICCE_ICL2B": PPD1_7_DATASET,
    "D_CE4A_ICLR4": PPD1_7_DATASET,
    "D_CE4A_ICLS4": PPD1_7_DATASET,
    "D_FDCE_I4": QM3_2_DATASET,
    "D_FDCE_I1": QM3_2_DATASET,
    "D_FDCE_I2": QM3_2_DATASET,
    "D_FDCE_H1": QM3_2_DATASET,
    "D_FDCE_H2": QM3_2_DATASET,
    "P_UAC_UACIP1": PPD1_3_DATASET,
    "P_UAC_UACIP2B": PPD1_3_DATASET,
    "P_UAC_UACIP4": PPD1_3_DATASET
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
    'P_OR_HC1': 'Continuation Questionnaire for England',
    'P_OR_HC2': 'Continuation Questionnaire for Wales (English)',
    'P_OR_HC2W': 'Continuation Questionnaire for Wales (Welsh)',
    'P_OR_HC4': 'Continuation Questionnaire for Northern Ireland (English)',
    "P_LP_HL1": 'Household Questionnaire Large Print pack for England',
    "P_LP_HL2": 'Household Questionnaire Large Print pack for Wales (English)',
    "P_LP_HL2W": 'Household Questionnaire Large Print pack for Wales (Welsh)',
    "P_LP_HL4": 'Household Questionnaire Large Print pack for Northern Ireland',
    "P_LP_ILP1": 'Individual Questionnaire (Large Print) for England',
    "P_LP_ILP2": 'Individual Questionnaire (Large Print) for Wales (in English)',
    "P_LP_ILP2W": 'Individual Questionnaire (Large Print) for Wales (in Welsh)',
    "P_LP_IL4": 'Individual Questionnaire (Large Print) for Northern Ireland',
    "P_TB_TBALB1": 'Translation Booklet for England - Albanian',
    "P_TB_TBAMH1": 'Translation Booklet for England - Amharic',
    "P_TB_TBARA1": 'Translation Booklet for England - Arabic',
    "P_TB_TBARA2": 'Translation Booklet for Wales - Arabic',
    "P_TB_TBARA4": 'Translation Booklet for Northern Ireland - Arabic',
    "P_TB_TBARM1": 'Translation Booklet for England - Armenian',
    "P_TB_TBBEN1": 'Translation Booklet for England - Bengali',
    "P_TB_TBBEN2": 'Translation Booklet for Wales - Bengali',
    "P_TB_TBBOS1": 'Translation Booklet for England - Bosnian',
    "P_TB_TBBUL1": 'Translation Booklet for England - Bulgarian',
    "P_TB_TBBUL2": 'Translation Booklet for Wales - Bulgarian',
    "P_TB_TBBUL4": 'Translation Booklet for Northern Ireland - Bulgarian',
    "P_TB_TBBUR1": 'Translation Booklet for England - Burmese',
    "P_TB_TBCAN1": 'Translation Booklet for England - Cantonese',
    "P_TB_TBCAN2": 'Translation Booklet for Wales - Cantonese',
    "P_TB_TBCAN4": 'Translation Booklet for Northern Ireland - Cantonese',
    "P_TB_TBCZE1": 'Translation Booklet for England - Czech',
    "P_TB_TBCZE4": 'Translation Booklet for Northern Ireland - Czech',
    "P_TB_TBFAR1": 'Translation Booklet for England - Farsi',
    "P_TB_TBFAR2": 'Translation Booklet for Wales - Farsi',
    "P_TB_TBFRE1": 'Translation Booklet for England - French',
    "P_TB_TBGER1": 'Translation Booklet for England - German',
    "P_TB_TBGRE1": 'Translation Booklet for England - Greek',
    "P_TB_TBGRE2": 'Translation Booklet for Wales - Greek',
    "P_TB_TBGUJ1": 'Translation Booklet for England - Gujarati',
    "P_TB_TBPAN1": 'Translation Booklet for England - Punjabi',
    "P_TB_TBPAN2": 'Translation Booklet for Wales - Punjabi',
    "P_TB_TBHEB1": 'Translation Booklet for England - Hebrew',
    "P_TB_TBHIN1": 'Translation Booklet for England - Hindi',
    "P_TB_TBHUN1": 'Translation Booklet for England - Hungarian',
    "P_TB_TBHUN4": 'Translation Booklet for Northern Ireland - Hungarian',
    "P_TB_TBIRI4": 'Translation Booklet for Northern Ireland - Irish',
    "P_TB_TBITA1": 'Translation Booklet for England - Italian',
    "P_TB_TBITA2": 'Translation Booklet for Wales - Italian',
    "P_TB_TBJAP1": 'Translation Booklet for England - Japanese',
    "P_TB_TBKOR1": 'Translation Booklet for England - Korean',
    "P_TB_TBKUR1": 'Translation Booklet for England - Kurdish',
    "P_TB_TBKUR2": 'Translation Booklet for Wales - Kurdish',
    "P_TB_TBLAT1": 'Translation Booklet for England - Latvian',
    "P_TB_TBLAT2": 'Translation Booklet for Wales - Latvian',
    "P_TB_TBLAT4": 'Translation Booklet for Northern Ireland - Latvian',
    "P_TB_TBLIN1": 'Translation Booklet for England - Lingala',
    "P_TB_TBLIT1": 'Translation Booklet for England - Lithuanian',
    "P_TB_TBLIT4": 'Translation Booklet for Northern Ireland - Lithuanian',
    "P_TB_TBMAL1": 'Translation Booklet for England - Malayalam',
    "P_TB_TBMAL2": 'Translation Booklet for Wales - Malayalam',
    "P_TB_TBMAN1": 'Translation Booklet for England - Mandarin Chinese',
    "P_TB_TBMAN2": 'Translation Booklet for Wales - Mandarin Chinese',
    "P_TB_TBMAN4": 'Translation Booklet for Northern Ireland - Mandarin Chinese',
    "P_TB_TBNEP1": 'Translation Booklet for England - Nepali',
    "P_TB_TBPAS1": 'Translation Booklet for England - Pashto',
    "P_TB_TBPAS2": 'Translation Booklet for Wales - Pashto',
    "P_TB_TBPOL1": 'Translation Booklet for England - Polish',
    "P_TB_TBPOL2": 'Translation Booklet for Wales - Polish',
    "P_TB_TBPOL4": 'Translation Booklet for Northern Ireland - Polish',
    "P_TB_TBPOR1": 'Translation Booklet for England - Portuguese',
    "P_TB_TBPOR2": 'Translation Booklet for Wales - Portuguese',
    "P_TB_TBPOR4": 'Translation Booklet for Northern Ireland - Portuguese',
    "P_TB_TBPOT1": 'Translation Booklet for England - Potwari',
    "P_TB_TBROM1": 'Translation Booklet for England - Romanian',
    "P_TB_TBROM4": 'Translation Booklet for Northern Ireland - Romanian',
    "P_TB_TBRUS1": 'Translation Booklet for England - Russian',
    "P_TB_TBRUS2": 'Translation Booklet for Wales - Russian',
    "P_TB_TBRUS4": 'Translation Booklet for Northern Ireland - Russian',
    "P_TB_TBSLE1": 'Translation Booklet for England - Slovenian',
    "P_TB_TBSLO1": 'Translation Booklet for England - Slovakian',
    "P_TB_TBSLO4": 'Translation Booklet for Northern Ireland - Slovakian',
    "P_TB_TBSOM1": 'Translation Booklet for England - Somali',
    "P_TB_TBSOM4": 'Translation Booklet for Northern Ireland - Somali',
    "P_TB_TBSPA1": 'Translation Booklet for England - Spanish',
    "P_TB_TBSPA2": 'Translation Booklet for Wales - Spanish',
    "P_TB_TBSWA1": 'Translation Booklet for England - Swahili',
    "P_TB_TBSWA2": 'Translation Booklet for Wales - Swahili',
    "P_TB_TBTAG1": 'Translation Booklet for England - Tagalog',
    "P_TB_TBTAM1": 'Translation Booklet for England - Tamil',
    "P_TB_TBTHA1": 'Translation Booklet for England - Thai',
    "P_TB_TBTHA2": 'Translation Booklet for Wales - Thai',
    "P_TB_TBTET4": 'Translation Booklet for Northern Ireland - Tetum',
    "P_TB_TBTIG1": 'Translation Booklet for England - Tigrinya',
    "P_TB_TBTUR1": 'Translation Booklet for England - Turkish',
    "P_TB_TBUKR1": 'Translation Booklet for England - Ukrainian',
    "P_TB_TBULS4": 'Translation Booklet for Northern Ireland - Ulster-Scots',
    "P_TB_TBURD1": 'Translation Booklet for England - Urdu',
    "P_TB_TBVIE1": 'Translation Booklet for England - Vietnamese',
    "P_TB_TBYSH1": 'Translation Booklet for England - Yiddish',
    "P_OR_I1": 'Individual Questionnaire for England',
    "P_OR_I2": 'Individual Questionnaire for Wales (in English)',
    "P_OR_I2W": 'Individual Questionnaire for Wales (in Welsh)',
    "P_OR_I4": 'Individual Questionnaire for Northern Ireland (in English)',
    "P_RL_1RL1_1": '1st Reminder, Letter - for England addresses',
    "P_RL_2RL2B_3a": '3rd Reminder, Letter - for Wales addresses',
    "P_QU_H1": '3rd Reminder, Questionnaire - for England addresses',
    "P_QU_H2": '3rd Reminder, Questionnaire - for Wales addresses',
    "P_QU_H4": '2nd Reminder, Questionnaire - for Ireland addresses',
    "P_RD_2RL1_1": "Response driven reminder group 1 English",
    "P_RD_2RL2B_1": "Response driven reminder group 1 Welsh",
    "P_RD_2RL1_2": "Response driven reminder group 2 English",
    "P_RD_2RL2B_2": "Response driven reminder group 2 Welsh",
    "P_RD_2RL1_3": "Response driven reminder group 3 English",
    "P_RD_2RL2B_3": "Response driven reminder group 3 Welsh",
    'P_UAC_UACHHP1': 'Household Unique Access Code for England via paper',
    'P_UAC_UACHHP2B': 'Household Unique Access Code for Wales (English/Welsh - Bilingual) via paper',
    'P_UAC_UACHHP4': 'Household Unique Access Code for Northern Ireland via paper',
    "D_CE1A_ICLCR1": "CE1 ICL with UAC for England (Hand Delivery) Addressed",
    "D_CE1A_ICLCR2B": "CE1 ICL with UAC for Wales (Hand Delivery) Addressed",
    "D_ICA_ICLR1": "Individual ICL with UAC for England (Hand Delivery) Addressed",
    "D_ICA_ICLR2B": "Individual ICL with UAC for Wales (Hand Delivery) Addressed",
    "P_ICCE_ICL1": 'Household ICL with UAC for England (Post Out) Addressed',
    "P_ICCE_ICL2B": 'Household ICL with UAC for Wales (Post Out) Addressed',
    "D_CE4A_ICLR4": "CE resident letter",
    "D_CE4A_ICLS4": "CE student letter",
    "D_FDCE_I4": "Individual Questionnaire for NI (Hand delivery) Addressed",
    "D_FDCE_I1": 'Individual Questionnaire for England (Hand delivery) Addressed',
    "D_FDCE_I2": 'Individual Questionnaire for Wales (Hand delivery) Addressed',
    "D_FDCE_H1": 'Household Questionnaire for England (Hand delivery) Addressed',
    "D_FDCE_H2": 'Household Questionnaire for Wales (Hand Delivery) Addressed',
    "P_ER_ILER1": 'Information leaflet (Easy Read) for England',
    "P_ER_ILER2B": 'Information leaflet (Easy Read) for Wales (English/Welsh - Bilingual)',
    "P_UAC_UACIP1": 'Individual Unique Access Code for England via paper',
    "P_UAC_UACIP2B": 'Individual Unique Access Code for Wales (English/Welsh - Bilingual) via paper',
    "P_UAC_UACIP4": 'Individual Unique Access Code for Northern Ireland via paper',
    "P_RL_1RL1A": '1st Reminder, Letter - for England addresses for survey launched but not completed',
    "P_RL_1RL2BA": '1st Reminder, Letter - for Wales addresses (bilingual Welsh and English) for survey'
                   ' launched but not completed',
    "P_RL_2RL1A": '2nd Reminder, Letter - for England addresses for survey launched but not completed',
    "P_RL_2RL2BA": '2nd Reminder, Letter - for Wales addresses (bilingual Welsh and English) for survey'
                   ' launched but not completed',
    "P_RL_1IRL1": 'Individual reminder letter - England',
    "P_RL_1IRL2B": 'Individual reminder letter - Bilingual',
}

QUESTIONNAIRE_TYPE_TO_FORM_TYPE = {
    "01": 'H',
    "02": 'H',
    "04": 'H',
    "21": 'I',
    "22": 'I',
    "24": 'I',
    "31": 'C',
    "32": 'C',
    "34": 'C',
}

NOTIFY_TEMPLATE = {
    # Household
    "UACHHT1": "ce1e545e-f50f-455b-a394-88b49a36fa0c",
    "UACHHT2": "2375c493-359d-4712-938e-bf97a641f18f",
    "UACHHT2W": "67dc02ff-a667-4b21-8e4e-61dd28936b8c",
    "UACHHT4": "5d985237-b446-492a-bd0a-f7368265282c",

    # Individual
    "UACIT1": "b7ec0cde-b55b-460a-a78a-cb80767acdca",
    "UACIT2": "f6de09f2-4d4c-4f62-82e3-b1a24e0cf910",
    "UACIT2W": "b2db05f0-d7d1-4b88-b3de-658495bd8a47",
    "UACIT4": "d490af7d-300a-4eb8-a961-cb4de54332ee",

    # CE
    "UACCET1": "21f22f8d-2642-444e-9d13-a54b87647a93",
    "UACCET2": "b2b9e650-cb22-49d7-b5da-95169e13ea12",
    "UACCET2W": "2c12a125-4035-4b81-9988-204e02e759a5"
}
