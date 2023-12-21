const AWS = require("aws-sdk");
AWS.config.update({ region: "ap-southeast-1" });
const sqs = new AWS.SQS();
var ddb = new AWS.DynamoDB({ apiVersion: "2023-01-24" });
var ses = new AWS.SES({ region: "ap-southeast-1" });
const s3 = new AWS.S3();
const axios = require("axios");

module.exports.handler = async (event) => {
  let stringifyRecord = JSON.stringify(event.Records?.[0]);
  let record = JSON.parse(stringifyRecord);
  const OldImage = record?.dynamodb?.OldImage;

  if (record?.eventName === "REMOVE") {
    if (
      OldImage?.sendMail?.BOOL === true &&
      OldImage?.reminder?.BOOL === false
    ) {
      const senderEmail = OldImage?.emailSchedule?.M?.senderEmail?.S;
      const receiverEmail = OldImage?.emailSchedule?.M?.receiverEmail?.S;
      const subject = OldImage?.emailSchedule?.M?.subject?.S;
      const message = OldImage?.emailSchedule?.M?.message?.S;
      const ccEmail = [];
      OldImage?.emailSchedule?.M?.ccEmail?.L?.forEach((item) => {
        const email = item?.S;
        if (email) {
          ccEmail.push(email);
        }
      });
      const response = await sendEmail(
        receiverEmail,
        ccEmail,
        senderEmail,
        message,
        subject
      );
    }

    if (OldImage?.orderStatus !== undefined && OldImage?.orderStatus !== null) {
      if (
        OldImage?.sendMail?.BOOL === true &&
        OldImage?.reminder?.BOOL === true
      ) {
        const intervalDays = OldImage?.intervalDays?.N;
        const currentEpochTime = Math.floor(new Date().getTime() / 1000);
        const IntervalDaysInSeconds = intervalDays * 24 * 60 * 60;
        const newEpochTime = currentEpochTime + IntervalDaysInSeconds;
        const epochTime = newEpochTime.toString();
        const params = {
          TableName: "EmailSchedule-prod",
          Item: {
            ...OldImage,
            timeToDelete: {
              N: epochTime,
            },
          },
        };
        const response = await ddb.putItem(params).promise();

        const loginUserGivenName =
          OldImage?.loginUser?.M?.loginUserGivenName?.S;
        const loginUserFamilyName =
          OldImage?.loginUser?.M?.loginUserFamilyName?.S;
        const loginUserEmail = OldImage?.loginUser?.M?.loginUserEmail?.S;
        const loginUserPhone = OldImage?.loginUser?.M?.loginUserPhone?.S;
        const moverName = OldImage?.loginUser?.M?.moverName?.S;
        const logoUrl = OldImage?.logoUrl?.S;
        const customerGivenName =
          OldImage?.emailSchedule?.M?.customerGivenName?.S;
        const fromCountry = OldImage?.emailSchedule?.M?.fromCountry?.S;
        const toCountry = OldImage?.emailSchedule?.M?.toCountry?.S;

        const quoteId = OldImage?.emailSchedule?.M?.quoteId?.S;
        const quoteUrl = OldImage?.emailSchedule?.M?.quoteUrl?.S;
        const uniqueId = OldImage?.emailSchedule?.M?.uniqueId?.S;
        const moverWebsite = OldImage?.loginUser?.M?.moverWebsite?.S;
        const orderId = OldImage?.orderId?.S;

        const senderEmail = OldImage?.emailSchedule?.M?.senderEmail?.S;
        const receiverEmail = OldImage?.emailSchedule?.M?.receiverEmail?.S;
        const subject = OldImage?.emailSchedule?.M?.subject?.S;
        const ccEmail = [];
        OldImage?.emailSchedule?.M?.ccEmail?.L?.forEach((item) => {
          const email = item?.S;
          if (email) {
            ccEmail.push(email);
          }
        });

        if (OldImage?.orderStatus?.S === "NEW") {
          const template = await getTemplateFromS3(
            "procyon-templates-prod",
            "Apac Relocation Pte Ltd/NewStateTemplate.txt"
          );
          const login_useremail = loginUserEmail;
          const message = template
            .replace("${loginUserGivenName}", loginUserGivenName)
            .replace("${loginUserFamilyName}", loginUserFamilyName)
            .replace("${loginUserPhone}", loginUserPhone)
            .replace("${loginUserEmail}", login_useremail)
            .replace("$loginUserEmail", login_useremail)
            .replace("${moverName}", moverName)
            .replace("${logo}", logoUrl)
            .replace("${givenName}", customerGivenName)
            .replace("${fromCountry}", fromCountry)
            .replace("${toCountry}", toCountry)
            .replace("${moverWebsite}", moverWebsite)
            .replace("$moverWebsite", moverWebsite);
          const response = await sendEmail(
            receiverEmail,
            ccEmail,
            senderEmail,
            message,
            subject
          );
          console.log(response);
        }

        if (OldImage?.orderStatus?.S === "CUSTOMER_QUOTE_ISSUED_STATE") {
          const template = await getTemplateFromS3(
            "procyon-templates-prod",
            "Apac Relocation Pte Ltd/QuoteIssuedStateTemplate.txt"
          );
          const pdf = await getPdfFromS3("quotefileupload-prod", quoteId);
          const login_useremail = loginUserEmail;
          const message = template
            .replace("$quoteId", quoteId)
            .replace("$uniqueId", uniqueId)
            .replace("$moverWebsite", moverWebsite)
            .replace("$quotePdfUrl", quoteUrl)
            .replace("$orderId", orderId)
            .replace("$loginUserGivenName", loginUserGivenName)
            .replace("$loginUserFamilyName", loginUserFamilyName)
            .replace("$loginUserPhone", loginUserPhone)
            .replace("${loginUserEmail}", login_useremail)
            .replace("$loginUserEmail", login_useremail)
            .replace("$moverName", moverName)
            .replace("${logo}", logoUrl)
            .replace("$givenName", customerGivenName)
            .replace("$fromCountry", fromCountry)
            .replace("$toCountry", toCountry)
            .replace("${moverWebsite}", moverWebsite)
            .replace("$moverWebsite", moverWebsite);

          const response = await sendEmailWithAttachment(
            receiverEmail,
            ccEmail,
            senderEmail,
            message,
            subject,
            pdf
          );
        }
      }
    }
  }

  async function getTemplateFromS3(bucket, filename) {
    try {
      // Retrieve the email template from S3
      const templateS3Params = {
        Bucket: bucket,
        Key: filename,
      };

      const templateObject = await s3.getObject(templateS3Params).promise();
      const emailTemplate = templateObject.Body.toString("utf-8");
      return emailTemplate;
    } catch {
      console.log("Unable to fetch template from s3");
    }
  }

  async function getPdfFromS3(bucket, key) {
    try {
      // Retrieve the email template from S3
      const templateS3Params = {
        Bucket: bucket,
        Key: key,
      };

      const templateObject = await s3.getObject(templateS3Params).promise();
      const emailTemplate = templateObject.Body.toString("base64");
      return emailTemplate;
    } catch {
      console.log("Unable to fetch pdf from s3");
    }
  }

  async function sendEmail(
    receiverEmail,
    ccEmail,
    senderEmail,
    template,
    subject
  ) {
    const mandrillApiKey = "B2KnJLwitNzIqMBPH-A9zg";
    const mandrillApiEndpoint =
      "https://mandrillapp.com/api/1.0/messages/send.json";
    const toEmails = ccEmail.map((email) => ({ email, type: "cc" }));
    const receiverEmailObject = {
      email: receiverEmail,
      type: "to",
    };
    toEmails.push(receiverEmailObject);

    const requestBody = {
      key: mandrillApiKey,
      message: {
        html: template,
        subject: subject,
        from_email: senderEmail,
        to: toEmails,
      },
    };

    try {
      const response = await axios.post(mandrillApiEndpoint, requestBody);

      // Print the response
      console.log(
        "Email sent! to : ",
        toEmails,
        "From : ",
        senderEmail,
        "In Order State:",
        OldImage?.orderStatus?.S
      );
      console.log("Response:", response);
    } catch (error) {
      // Handle errors
      console.error("Error:", error.message);
    }
  }

  async function sendEmailWithAttachment(
    receiverEmail,
    ccEmail,
    senderEmail,
    template,
    subject,
    attachment
  ) {
    const mandrillApiKey = "B2KnJLwitNzIqMBPH-A9zg";
    const mandrillApiEndpoint =
      "https://mandrillapp.com/api/1.0/messages/send.json";
    const toEmails = ccEmail.map((email) => ({ email, type: "cc" }));
    const receiverEmailObject = {
      email: receiverEmail,
      type: "to",
    };
    toEmails.push(receiverEmailObject);

    const requestBody = {
      key: mandrillApiKey,
      message: {
        html: template,
        subject: subject,
        from_email: senderEmail,
        to: toEmails,
        attachments: [
          {
            type: "application/pdf",
            name: "Quote.pdf",
            content: attachment,
          },
        ],
      },
    };

    try {
      const response = await axios.post(mandrillApiEndpoint, requestBody);

      // Print the response
      console.log(
        "Email sent! to",
        toEmails,
        "From",
        senderEmail,
        "In Order State:",
        OldImage?.orderStatus.S
      );
      console.log("Response:", response.data);
    } catch (error) {
      // Handle errors
      console.error("Error:", error.message);
    }
  }
};
