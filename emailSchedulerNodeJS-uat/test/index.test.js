const index = require("../index");
// const {assert} = require('chai');
// const sinon = require('sinon');
const payload = {
  Records: [
    {
      eventID: "bcecaf026b76569adf455645141199c9",
      eventName: "REMOVE",
      eventVersion: "1.1",
      eventSource: "aws:dynamodb",
      awsRegion: "ap-southeast-1",
      dynamodb: {
        ApproximateCreationDateTime: 1701329731,
        Keys: { orderId: [Object], scheduleId: [Object] },
        OldImage: {
          scheduleId: {
            S: "30112023_073853_000655",
          },
          orderId: {
            S: "16112023_054803_000491",
          },
          emailSchedule: {
            M: {
              ccEmail: {
                L: [
                  {
                    S: "vaishnavijayakumar19@gmail.com",
                  },
                ],
              },
              customerFamilyName: {
                S: "Test",
              },
              customerGivenName: {
                S: "Prajual",
              },
              fromCountry: {
                S: "United Arab Emirates",
              },
              message: {
                S: "<p>Dear ,</p><p>Thank you for your time to discuss about the moving requirement.</p><p>We would like to confirm the PreMove Survey on Thursday, September 28, 2023 11:00 PM at your address 30 Raffles Ave., Singapore 039803.</p><p>thanks&nbsp;</p><p>&nbsp;</p>",
              },
              quoteFollowUp: {
                BOOL: true,
              },
              quoteId: {
                S: "16112023_055221_000822",
              },
              quoteUrl: {
                S: "https://quotefileupload.s3.ap-southeast-1.amazonaws.com/16112023_055221_000822",
              },
              receiverEmail: {
                S: "prajualnandu@gmail.com",
              },
              senderEmail: {
                S: "info@moversly.com",
              },
              subject: {
                S: "Moving Quote From Dubai,United Arab Emirates To Dubai,United Arab Emirates | Moversly Test Account",
              },
              toCountry: {
                S: "United Arab Emirates",
              },
              uniqueId: {
                S: "2b6c1144-2ff5-4379-9e7e-f3054e26b9e7-8d14f45c-9e54-464e-b908-34cfd4d9b919-b4d5fc60-bbd3-4c1a-92ca-cef8e24553cb",
              },
            },
          },
          intervalDays: {
            N: "2",
          },
          loginUser: {
            M: {
              loginUserEmail: {
                S: "info@moversly.com",
              },
              loginUserFamilyName: {
                S: "Apac",
              },
              loginUserGivenName: {
                S: "Test Sales",
              },
              loginUserPhone: {
                S: "+919495792118",
              },
              moverName: {
                S: "Moversly Test Account",
              },
              moverWebsite: {
                S: "admin-dev.moversly.com",
              },
            },
          },
          logoUrl: {
            S: "https://moveradminfileupload.s3.ap-southeast-1.amazonaws.com/04584928-7495-4e91-ae7f-b8194814037f/41b1ab18-dd5e-469e-9b88-1c704220344d",
          },
          reminder: {
            BOOL: true,
          },
          sendMail: {
            BOOL: true,
          },
          timeToDelete: {
            N: "1701502733",
          },
        },
        SequenceNumber: "398036300000000038576652201",
        SizeBytes: 4809,
        StreamViewType: "NEW_AND_OLD_IMAGES",
      },
      eventSourceARN:
        "arn:aws:dynamodb:ap-southeast-1:978606118148:table/EmailSchedule-uat/stream/2023-09-11T04:39:13.978",
    },
  ],
};

describe("sqs event", () => {
  it("sunny day scenario", (done) => {
    index
      .handler(payload, "")
      .then((data) => {
        console.log(data);
        done();
      })
      .catch((error) => {
        console.log(error);
      });
  });
});
