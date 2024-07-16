const Test = require('../models/test');
const User = require('../models/user');
const shortid = require('shortid');

const createTest = (req, res) => {
    const { email, organizationName, testName, testLink, startTime, duration, totalCandidates,keywords } = req.body;

    const [datePart, timePart] = startTime.split(' - ');
    const [month, day, year] = datePart.split('/');
    const [hours, minutes] = timePart.split(':');

    const parsedStartTime = new Date(`20${year}`, month - 1, day, hours, minutes);

    const end_time = new Date(parsedStartTime);
    end_time.setMinutes(end_time.getMinutes() + parseInt(duration));
    const keywordArray = keywords.split(' ').map(keyword => keyword.trim()).filter(keyword => keyword)
    const test = new Test({
        userId: req.user.id,
        email: email,
        test_name: testName,
        test_link_by_user: testLink,
        test_code: shortid.generate() + "-" + shortid.generate(),
        start_time: parsedStartTime,
        end_time: end_time,
        no_of_candidates_appear: totalCandidates,
        total_threshold_warnings: 3,
        keywords:keywordArray
    });

    test.save((error, data) => {
        if (error) {
            if (error.code === 11000) {
                // Duplicate key error
                return res.json({ msg: "A test with this link already exists", error });
            }
            return res.json({ msg: "Something happened while creating new test", error });
        }
        if (data) {
            return res.status(201).json({ msg: "Successfully created new Test on platform" , data});
        }
    });
};

const userCreatedTests = (req, res) => {
    const userId = req.user.id;
    if (userId) {
        Test.find({ userId: userId })
            .exec((error, _allTests) => {
                if (error) return res.status(400).json({ msg: "Something went wrong while fetching user tests", error })
                if (_allTests) return res.status(200).json({ _allTests })
            })
    } else {
        return res.status(400).json({
            msg: {
                one: "check user id, something wrong with it",
                two: "can't pass empty userId"
            }
        })
    }
}

const createdTests = async (req,res) => {
    const email = req.query.email;
    try {
        const tests = await Test.find({email});
        console.log(tests)
        return res.json(tests);
    } catch (error) {
        console.log(error);
        return res.json(error);
    }

}

const testRegister = async (req, res) => {
    const { test_code } = req.params;
    const userId = req.user.id;
    if (userId) {
        const updateData = await User.findOneAndUpdate({ _id: userId }, {
            test_code: test_code
        });
        // res.status(200).json({ updateData });
        res.status(200).json({ msg: "Now you are register" })
    }
}

const testAdminData = (req, res) => {
    const { test_code } = req.params;
    if (test_code) {
        User.find({ test_code: test_code })
            .exec((error, candidates) => {
                if (error) return res.status(400).json({ msg: "Something went wrong while fetching candidates-status" });
                if (candidates) return res.status(200).json({ candidates })
            })
    }
}

const increasePersonDetected = async (req, res) => {
    const userId = req.user.id;
    if (userId) {
        const updateData = await User.findOneAndUpdate({ _id: userId }, {
            $inc: { person_detected: 1 }
        })
        res.status(200).json({ msg: "warning of person detected" });
    }
}

const increaseVoiceDetected = async (req, res) => {
    const userId = req.user.id;
    if (userId) {
        const updateData = await User.findOneAndUpdate({ _id: userId }, {
            $inc: { voice_detected: 1 }
        })
        res.status(200).json({ msg: "warning of voice detected" });
    }
}

const increaseFaceCovering = async (req, res) => {
    const userId = req.user.id;
    if (userId) {
        const updateData = await User.findOneAndUpdate({ _id: userId }, {
            $inc: { face_covered: 1 }
        })
        res.status(200).json({ msg: "warning for face covering" });
    }
}

const totalWarnings = (req, res) => {
    const userId = req.user.id;
    if (userId) {
        User.findOne({ _id: userId })
            .exec((error, data) => {
                if (data) {
                    let total_warnings = data.person_detected + data.voice_detected + data.face_covered;
                    return res.status(200).json({ totalWarnings: total_warnings })
                }
            })
    } else {
        return res.status(200).json({ msg: "check user-id" });
    }
}

const terminateExam = async (req, res) => {
    const userId = req.user.id;
    if (userId) {
        const updateData = await User.findOneAndUpdate({ _id: userId }, {
            status: "block"
        });
        // res.status(200).json({ updateData });
        res.status(200).json({ msg: "candidate has been blocked" })
    }
}

const allowInExam = async (req, res) => {
    const userId = req.user.id;
    if (userId) {
        const updateData = await User.findOneAndUpdate({ _id: userId }, {
            status: "safe"
        });
        // res.status(200).json({ updateData });
        res.status(200).json({ msg: "candidate is now allowed to give exam" })
    }
}

const getTestDetails = async (req, res) => {
    const { test_code } = req.params;
    try {
        const test = await Test.findOne({ test_code });
        if (!test) {
            return res.json({ msg: "Test not found" });
        }
        res.status(200).json(test);
    } catch (error) {
        res.status(500).json({ msg: "Error fetching test details", error });
    }
};

const allTests = async (req,res) =>{
    try {
        const test = await Test.find({ });
        if (!test) {
            return res.json({ msg: "Test not found" });
        }
        res.status(200).json(test);
    } catch (error) {
        res.status(500).json({ msg: "Error fetching test details", error });
    }
}

const getKeywords = async (req, res) =>{
    const { testCode } = req.query;
    try {
        const test = await Test.findOne({ test_code: testCode });
        if (!test) {
            return res.json({ msg: "Test not found" });
        }
        console.log(test.keywords);
        res.json({ keywords: test.keywords });
    } catch (error) {
        res.status(500).json({ msg: "Error fetching test details", error });
    }
}

const getAttemptedTestNames = async (req, res) =>{
    const { testCodes } = req.body;

  try {
    const matchingTests = await Test.find({
      test_code: { $in: testCodes }
    });
    res.json(matchingTests);
  } catch (err) {
    res.status(500).json({ error: 'Server error' });
  }
}

const updateTests = async (req, res) =>{
    const {testCode, formData} = req.body;
    const {testName, testLink, startTime, duration, totalCandidates, keywords } = formData;

  try {
    // Convert duration back to endTime
    const startTimeDate = new Date(startTime);
    const endTimeDate = new Date(startTimeDate.getTime() + duration * 60000); // duration is in minutes

    const keywordsArray = keywords.split(" ");

    const test = await Test.findOneAndUpdate(
      { test_code: testCode },
      {        
        test_name: testName,
        test_link_by_user: testLink,
        start_time: startTimeDate,
        end_time: endTimeDate,
        no_of_candidates_appear:totalCandidates,
        keywords: keywordsArray,
      },
      { new: true }
    );

    if (!test) {
      return res.status(404).json({ msg: "Test not found" });
    }

    res.status(201).json({ msg: "Test updated successfully", data: { test } });
  } catch (error) {
    console.error("There was an error updating the test!", error);
    res.status(500).json({ msg: "Internal server error" });
  }
}

module.exports = {
    createTest,
    userCreatedTests,
    testRegister,
    testAdminData,
    increasePersonDetected,
    increaseVoiceDetected,
    increaseFaceCovering,
    increasePersonDetected,
    increaseVoiceDetected,
    increaseFaceCovering,
    totalWarnings,
    terminateExam,
    allowInExam,
    getTestDetails,
    allTests,
    createdTests,
    getKeywords,
    getAttemptedTestNames,
    updateTests,
}